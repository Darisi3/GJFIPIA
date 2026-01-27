# scraper_service.py - VERSION I KORRIGJUAR
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
import json
from config import config

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
    print("[SCRAPER] Playwright u importua me sukses!")
except Exception as e:
    PLAYWRIGHT_AVAILABLE = False
    sync_playwright = None
    print(f"[SCRAPER] Playwright nuk u importua: {e}")

try:
    from services.ocr_service import OCRService
    OCR_AVAILABLE = True
    print("[SCRAPER] OCRService u importua me sukses!")
except Exception as e:
    OCR_AVAILABLE = False
    print(f"[SCRAPER] OCRService nuk u importua: {e}")


class ScraperService:
    @staticmethod
    def scrape_newspaper_articles(url, max_articles=10):
        """
        Skrap artikujt nga një faqe gazete
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Kontrollo encoding
            if response.encoding is None:
                response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding=response.encoding)

            # Heq script dhe style elementet
            for script in soup(["script", "style", "noscript", "meta", "link"]):
                script.decompose()

            article_selectors = [
                'article', '.article', '.news-item', '.post', '.news',
                'h1', 'h2', 'h3', '.title', '.headline', '.news-title',
                '.entry-title', '.post-title', '.item-title'
            ]
            
            articles = []
            seen_texts = set()
            
            for selector in article_selectors:
                elements = soup.select(selector)
                for elem in elements[:max_articles * 2]:  # Merr më shumë për të filtruar
                    text = elem.get_text(strip=True)
                    
                    # Filtro artikujt e dobët
                    if len(text) > 50 and text not in seen_texts:
                        seen_texts.add(text)
                        
                        # Gjej linkun
                        link = None
                        if elem.name == 'a' and elem.get('href'):
                            link = urljoin(url, elem.get('href'))
                        else:
                            # Kërko për link brenda elementit
                            link_elem = elem.find('a', href=True)
                            if link_elem:
                                link = urljoin(url, link_elem.get('href'))
                        
                        articles.append({
                            'title': text[:150],
                            'url': link or url,
                            'preview': text[:250] + '...' if len(text) > 250 else text,
                            'length': len(text)
                        })
                        
                        if len(articles) >= max_articles:
                            break
                
                if len(articles) >= max_articles:
                    break

            return {
                'success': True, 
                'articles': articles[:max_articles], 
                'count': len(articles),
                'url': url
            }
            
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Gabim në lidhje: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'Gabim i përgjithshëm: {str(e)}'}

    @staticmethod
    def _score_result(ocr_search, search_text, full_text):
        """
        Llogarit pikën për një rezultat bazuar në ndeshjet OCR dhe tekstin
        """
        score = 0
        
        # Shto pikë për ndeshjet OCR
        if ocr_search.get('matches'):
            matches = ocr_search['matches']
            score += len(matches) * 10
            
            # Shto pikë për besueshmërinë mesatare
            confidences = [m.get('confidence', 0) for m in matches if m.get('confidence')]
            if confidences:
                score += sum(confidences) / len(confidences)
        
        # Shto pikë nëse fjala gjendet në tekstin e plotë të faqes
        if search_text and full_text and search_text.lower() in full_text.lower():
            # Numëro sa herë shfaqet
            occurrences = full_text.lower().count(search_text.lower())
            score += occurrences * 5
        
        # Bonus për ndeshje të sakta
        if ocr_search.get('success') and ocr_search.get('matches'):
            for match in ocr_search['matches']:
                if match.get('text', '').lower() == search_text.lower():
                    score += 20
        
        return round(score, 2)

    @staticmethod
    def _extract_links(soup, base_url, max_links=10):
        """
        Nxjerr linket nga një faqe
        """
        links = []
        seen = set()
        
        # Së pari, kërko për linke që duken si artikuj
        article_selectors = [
            'a[href*="article"]', 'a[href*="news"]', 'a[href*="post"]',
            'a[href*="story"]', 'a[href*="blog"]', '.article a',
            '.news-item a', '.post a'
        ]
        
        for selector in article_selectors:
            for a in soup.select(selector):
                href = a.get('href', '')
                if href and not href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                    full_url = urljoin(base_url, href)
                    if full_url not in seen:
                        seen.add(full_url)
                        links.append({
                            'url': full_url,
                            'text': a.get_text(strip=True)[:100],
                            'is_article': True
                        })
                        if len(links) >= max_links:
                            return links
        
        # Nëse nuk mjaftojnë, merr çdo link
        for a in soup.find_all('a', href=True):
            if len(links) >= max_links:
                break
                
            href = a['href']
            if href and not href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                full_url = urljoin(base_url, href)
                if full_url not in seen:
                    seen.add(full_url)
                    links.append({
                        'url': full_url,
                        'text': a.get_text(strip=True)[:100],
                        'is_article': False
                    })
        
        return links

    @staticmethod
    def scrape_and_screenshots(url, search_text, max_pages=5):
        """
        Kryen skrapimin dhe marrjen e screenshot-eve
        """
        try:
            print(f"\n[SCRAPER] Duke filluar skrapim për: {url}")
            print(f"[SCRAPER] Duke kërkuar fjalën: '{search_text}'")
            print(f"[SCRAPER] Numri maksimal i faqeve: {max_pages}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            # Merr faqen kryesore
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            
            # Kontrollo encoding
            if resp.encoding is None:
                resp.encoding = 'utf-8'
            
            soup = BeautifulSoup(resp.content, 'html.parser', from_encoding=resp.encoding)
            
            # Nxjerr linket
            links_data = ScraperService._extract_links(soup, url, max_pages)
            links = [item['url'] for item in links_data]
            
            print(f"[SCRAPER] U gjetën {len(links)} linke")
            
            # Nëse nuk ka Playwright, përdor fallback HTML
            if not PLAYWRIGHT_AVAILABLE:
                print("[SCRAPER] Playwright nuk është i disponueshëm – përdoret fallback HTML.")
                results = ScraperService._fallback_html_scrape(links, search_text, headers)
                return {'success': True, 'results': results}
            
            # Përdor Playwright për screenshot
            print("[SCRAPER] Duke nisur Playwright...")
            
            results = []
            
            with sync_playwright() as pw:
                # Konfiguro browser
                browser = pw.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--start-maximized'
                    ]
                )
                
                context = browser.new_context(
                    ignore_https_errors=True,
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080},
                    device_scale_factor=2  # Rrit rezolucionin për tekst më të qartë
                )
                
                # Shto headers shtesë
                context.set_extra_http_headers({
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                })
                
                # Krijo folder për screenshot
                screenshots_dir = os.path.join(config.UPLOAD_FOLDER, 'screenshots')
                os.makedirs(screenshots_dir, exist_ok=True)
                
                # Proceso çdo link
                for i, page_url in enumerate(links[:max_pages]):
                    try:
                        print(f"\n[SCRAPER] [{i+1}/{len(links[:max_pages])}] Duke përpunuar: {page_url}")
                        
                        page = context.new_page()
                        
                        # Navigo në faqe
                        try:
                            response = page.goto(
                                page_url, 
                                wait_until='networkidle', 
                                timeout=45000  # Rrit timeout-in
                            )
                            
                            if response and response.status >= 400:
                                print(f"[SCRAPER] Faqja ktheu status {response.status}")
                                page.close()
                                continue
                                
                        except Exception as nav_error:
                            print(f"[SCRAPER] Gabim në navigim: {nav_error}")
                            page.close()
                            continue
                        
                        # Prit që faqja të ngarkohet plotësisht
                        page.wait_for_timeout(4000)  # Rrit kohën e pritjes
                        
                        # Merr tekstin e faqes për analizë
                        full_text = page.inner_text('body')
                        print(f"[SCRAPER] Faqja përmban {len(full_text)} karaktere tekst")
                        
                        # Krijo emrin unik për screenshot
                        timestamp = int(time.time())
                        domain = urlparse(page_url).netloc.replace('.', '_')
                        filename = f"screenshot_{domain}_{timestamp}_{i}.png"
                        save_path = os.path.join(screenshots_dir, filename)
                        
                        # Merr screenshot
                        try:
                            # Së pari, provo të marrësh screenshot të plotë
                            page.screenshot(
                                path=save_path,
                                full_page=True,
                                timeout=30000,
                                type='png'
                            )
                            print(f"[SCRAPER] Screenshot i ruajtur: {save_path}")
                        except Exception as screenshot_error:
                            print(f"[SCRAPER] Gabim me full_page screenshot: {screenshot_error}")
                            # Provo vetëm viewport
                            try:
                                page.screenshot(
                                    path=save_path,
                                    full_page=False,
                                    timeout=20000,
                                    type='png'
                                )
                                print(f"[SCRAPER] Screenshot viewport u ruajtur")
                            except Exception as e2:
                                print(f"[SCRAPER] Dështoi edhe viewport screenshot: {e2}")
                                page.close()
                                continue
                        
                        # Bëj OCR nëse është i disponueshëm
                        ocr_search = {'success': False, 'matches': []}
                        
                        if OCR_AVAILABLE and os.path.exists(save_path):
                            # Përcakto gjuhën bazuar në URL
                            if any(domain in page_url for domain in ['.al', '.ks', 'shqip', 'botasot']):
                                language = 'sqi'
                            else:
                                language = 'eng'
                            
                            print(f"[OCR] Duke kërkuar '{search_text}' në gjuhën {language}...")
                            
                            try:
                                ocr_search = OCRService.search_text_in_image(save_path, search_text, language=language)
                                
                                if ocr_search.get('success'):
                                    matches = ocr_search.get('matches', [])
                                    print(f"[OCR] U gjetën {len(matches)} përputhje")
                                    
                                    if matches:
                                        for match in matches[:3]:  # Print vetëm 3 të parat
                                            text_preview = match.get('text', '')[:50]
                                            conf = match.get('confidence', 0)
                                            print(f"  - '{text_preview}'... (besueshmëri: {conf}%)")
                                else:
                                    print(f"[OCR] OCR dështoi: {ocr_search.get('error', 'Gabim i panjohur')}")
                                    
                            except Exception as ocr_error:
                                print(f"[OCR] Gabim në OCR: {ocr_error}")
                                ocr_search = {'success': False, 'error': str(ocr_error), 'matches': []}
                        else:
                            print(f"[OCR] OCR nuk është i disponueshëm ose screenshot nuk ekziston")
                        
                        # Llogarit pikën
                        score = ScraperService._score_result(ocr_search, search_text, full_text)
                        
                        # Krijo rezultatin
                        result = {
                            'page_url': page_url,
                            'screenshot_path': save_path,
                            'screenshot_url': f"/static/uploads/screenshots/{filename}",
                            'score': score,
                            'text_preview': full_text[:200] + '...' if len(full_text) > 200 else full_text,
                            'text_length': len(full_text),
                            'ocr': ocr_search
                        }
                        
                        # Shto në rezultatet edhe nëse nuk ka ndeshje OCR
                        # por vetëm nëse fjala gjendet në tekstin e faqes
                        if ocr_search.get('matches') or search_text.lower() in full_text.lower():
                            results.append(result)
                            print(f"[SCRAPER] Rezultati u shtua me pikë: {score}")
                        else:
                            print(f"[SCRAPER] Nuk u gjet fjala në tekst, rezultati nuk u shtua")
                        
                        page.close()
                        time.sleep(1)  # Pauzë e shkurtër midis faqeve
                        
                    except Exception as page_error:
                        print(f"[SCRAPER] Gabim i përgjithshëm në faqe {page_url}: {page_error}")
                        results.append({
                            'page_url': page_url,
                            'error': str(page_error),
                            'score': 0,
                            'ocr': {'success': False, 'matches': []}
                        })
                
                browser.close()
            
            # Rendit rezultatet sipas pikës
            results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            # Filtro rezultatet me pikë më të lartë se 0 ose me ndeshje
            filtered_results = [r for r in results if r.get('score', 0) > 0 or 
                              (r.get('ocr', {}).get('matches', []))]
            
            print(f"\n[SCRAPER] Përfundoi! Gjithsej {len(filtered_results)} rezultate me ndeshje")
            
            return {
                'success': True,
                'results': filtered_results,
                'search_info': {
                    'query': search_text,
                    'url': url,
                    'total_pages_scraped': len(links[:max_pages]),
                    'total_matches': sum(len(r.get('ocr', {}).get('matches', [])) for r in filtered_results),
                    'results_count': len(filtered_results)
                }
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Gabim në lidhje me {url}: {str(e)}"
            print(f"[SCRAPER] {error_msg}")
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Gabim i përgjithshëm: {str(e)}"
            print(f"[SCRAPER] {error_msg}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': error_msg}

    @staticmethod
    def _fallback_html_scrape(links, search_text, headers):
        """
        Metodë fallback për skrapim pa Playwright
        """
        results = []
        
        for i, page_url in enumerate(links):
            try:
                print(f"[SCRAPER] [{i+1}/{len(links)}] Duke përpunuar (HTML fallback): {page_url}")
                
                r = requests.get(page_url, headers=headers, timeout=15)
                r.raise_for_status()
                
                # Kontrollo encoding
                if r.encoding is None:
                    r.encoding = 'utf-8'
                
                soup = BeautifulSoup(r.content, 'html.parser', from_encoding=r.encoding)
                
                # Heq elementet e padëshiruara
                for script in soup(["script", "style", "noscript", "meta", "link"]):
                    script.decompose()
                
                text_body = soup.get_text(separator=' ', strip=True)
                
                # Kontrollo nëse fjala gjendet
                found = search_text.lower() in text_body.lower()
                
                # Krijo snippet nëse gjendet
                snippet = ''
                if found:
                    idx = text_body.lower().find(search_text.lower())
                    start = max(0, idx - 120)
                    end = min(len(text_body), idx + 120)
                    snippet = text_body[start:end]
                
                # Numëro sa herë shfaqet
                occurrences = text_body.lower().count(search_text.lower())
                
                # Llogarit pikën
                score = occurrences * 5
                
                # Krijo rezultatin
                result = {
                    'page_url': page_url,
                    'screenshot_path': None,
                    'screenshot_url': None,
                    'score': score,
                    'text_preview': text_body[:200] + '...' if len(text_body) > 200 else text_body,
                    'text_length': len(text_body),
                    'ocr': {
                        'success': True,
                        'matches': [] if not found else [{
                            'text': snippet,
                            'bbox': None,
                            'confidence': 100.0
                        }]
                    }
                }
                
                results.append(result)
                print(f"[SCRAPER] Faqja përmban fjalën {occurrences} herë, pikë: {score}")
                
            except Exception as e:
                print(f"[SCRAPER] Gabim në {page_url}: {e}")
                results.append({
                    'page_url': page_url,
                    'error': str(e),
                    'score': 0,
                    'ocr': {'success': False, 'matches': []}
                })
        
        return results

    @staticmethod
    def validate_url(url):
        """
        Validon një URL përpara se të fillojë skrapimi
        """
        try:
            parsed = urlparse(url)
            if not parsed.scheme:
                url = 'http://' + url
                parsed = urlparse(url)
            
            if not parsed.netloc:
                return False, "URL jo e vlefshme: mungon domain"
            
            # Kontrollo nëse është URL e zakonshme web
            if parsed.scheme not in ['http', 'https']:
                return False, "URL duhet të jetë HTTP ose HTTPS"
            
            return True, url
            
        except Exception as e:
            return False, f"Gabim në validimin e URL: {str(e)}"

    @staticmethod
    def save_results_to_file(results, filename=None):
        """
        Ruaj rezultatet në një file JSON për referencë
        """
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"scraping_results_{timestamp}.json"
            
            # Krijo folder për rezultatet nëse nuk ekziston
            results_dir = os.path.join(config.UPLOAD_FOLDER, 'results')
            os.makedirs(results_dir, exist_ok=True)
            
            filepath = os.path.join(results_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"[SCRAPER] Rezultatet u ruajtën në: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"[SCRAPER] Gabim në ruajtjen e rezultateve: {e}")
            return None