from flask import Blueprint, render_template, request
from .utils import create_dataframe, save_data_plot, get_channel_details

bp = Blueprint('main', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    error_message = None
    channel_details = None
    data = None

    if request.method == 'POST':
        channel_id = request.form['channel_id']
        try:
            data = create_dataframe(channel_id)
            channel_details = get_channel_details(channel_id)
            save_data_plot(data, plot_type='views')
            save_data_plot(data, plot_type='likes')

        except ValueError as e:
            error_message = str(e)
        except Exception as e:
            error_message = str(e)
            print(f"Error: {e}")

    return render_template("dashboard.html", channel_details=channel_details, data=data, error_message=error_message)
