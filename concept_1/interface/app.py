from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, create_engine

app = Flask(__name__)

# Create SQLAlchemy engines
engine_eplf = create_engine('postgresql://postgres:postgres@192.168.0.23:5432/db')
engine_zd = create_engine('postgresql://postgres:postgres@192.168.0.24:5432/db')

@app.route('/')
def home():
    return render_template('index.html')



@app.route('/update_data')
def update_data():

    try:
        # EPLF Payments (all)
        with engine_eplf.connect() as connection:
            result_eplf = connection.execute(text("SELECT COUNT(*) FROM Payments"))
            eplf_payment_all = result_eplf.fetchone()[0]

        # EPLF Log (all)
        with engine_eplf.connect() as connection:
            result_eplf = connection.execute(text("SELECT COUNT(*) FROM Log"))
            eplf_log_all = result_eplf.fetchone()[0]

        # EPLF Log (faulty)
        with engine_eplf.connect() as connection:
            result_eplf = connection.execute(text("SELECT COUNT(*) FROM Log WHERE faulty='True'"))
            eplf_log_faulty = result_eplf.fetchone()[0]

        # EPLF Log (validated)
        with engine_eplf.connect() as connection:
            result_eplf = connection.execute(text("SELECT COUNT(*) FROM Log WHERE validated='True'"))
            eplf_log_validated = result_eplf.fetchone()[0]

        # ZD Payments (all)
        with engine_zd.connect() as connection:
            result_zd = connection.execute(text("SELECT COUNT(*) FROM Payments"))
            zd_payment_all = result_zd.fetchone()[0]

        return jsonify({
                        'eplf_payment_all': eplf_payment_all,
                        'eplf_log_all': eplf_log_all,
                        'eplf_log_faulty': eplf_log_faulty,
                        'eplf_log_validated': eplf_log_validated,
                        'zd_payment_all': zd_payment_all,
        })

    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
