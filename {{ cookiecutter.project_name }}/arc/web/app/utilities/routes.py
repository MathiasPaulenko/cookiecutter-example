from flask import request, jsonify

from arc.settings.settings_manager import Settings
from arc.web.app.utilities import bp as utilities_bp


@utilities_bp.route("/utils/feature", methods=['POST'])
def get_feature_data():
    """
    This view return the complete text of a feature file.
    :return:
    """
    feature_path = request.data.decode()
    feature_data = ""
    if Settings.TEST_PATH.get(force=True) in feature_path:
        with open(feature_path, 'r') as f:
            feature_data = f.read()
    return jsonify(feature_data)
