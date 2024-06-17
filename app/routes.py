from flask import Blueprint, render_template, request
from .utils import create_dataframe, save_data_plot, get_channel_details

bp = Blueprint('main', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        channel_id = request.form['channel_id']
        data = create_dataframe(channel_id)
        channel_details = get_channel_details(channel_id)
        save_data_plot(data, plot_type='views')
        save_data_plot(data, plot_type='likes')
        return render_template("dashboard.html",
                               channel_details=channel_details,
                               data=data.to_html(classes='data', header=True, index=False))

    return render_template("dashboard.html", channel_details=None,data=None)
