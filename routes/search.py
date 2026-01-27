from flask import Blueprint, request, jsonify
from services.scraper_service import ScraperService
from config import config          # ← importo config (nëse duhet path-i)

search_bp = Blueprint('search', __name__)

@search_bp.route('/ping', methods=['GET'])
def ping():
    """Health-check për të konfirmuar që blueprint-i është online"""
    return jsonify({'message': 'search blueprint online'}), 200

@search_bp.route('/scrape', methods=['POST'])
def scrape():
    """
    Pranon JSON me:
      url, text, max_pages (opsional)
    Kthen JSON me:
      success, data (listë me screenshots & matches), error
    """
    try:
        data = request.get_json() or {}
        url = data.get('url')
        text = data.get('text')
        max_pages = int(data.get('max_pages', 5))

        if not url or not text:
            return jsonify({'success': False, 'error': 'Mungon URL ose fjala për kërkim'}), 400

        # Thirr funksionin që ke në ScraperService
        result = ScraperService.scrape_and_screenshots(url, text, max_pages=max_pages)

        if not result.get('success'):
            return jsonify({'success': False, 'error': result.get('error', 'Gabim i panjohur')}), 500

        return jsonify({'success': True, 'data': result.get('results', [])}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500