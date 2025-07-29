from flask import Flask,render_template,request,url_for,redirect,Response
from flask_sqlalchemy import SQLAlchemy
import io
from io import TextIOWrapper
import csv
from sqlalchemy.sql import text
from sqlalchemy import PrimaryKeyConstraint

app = Flask(__name__)
app.secret_key = "secret_key"

app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database2.db' 

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class Data(db.Model):
    __tablename__ = 'stations'
    vin = db.Column(db.String(128), primary_key=True)
    manufacturer = db.Column(db.String(128), nullable = False)
    model = db.Column(db.String(128), nullable = False)
    owner = db.Column(db.String(128), nullable = False)
    fid = db.Column(db.String(128), nullable = False)
    reg_status = db.Column(db.String(128), nullable = False)
    

    def __init__(self,vin,manufacturer,model,owner,fid,reg_status):
 
        self.vin = vin
        self.manufacturer = manufacturer
        self.model = model
        self.owner=owner
        self.fid=fid
        self.reg_status = reg_status

class Telemetry(db.Model):
    __tablename__ = 'telemetry'
    vin =db.Column(db.String(128), primary_key=True)
    timestamp=db.Column(db.String(128), primary_key=True)
    latitude= db.Column(db.String(128), nullable=False)
    longitude= db.Column(db.String(128), nullable=False)
    battery=db.Column(db.Integer, nullable=False)
    odometer=db.Column(db.Integer, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('vin','timestamp'),
    )

class Alert(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    vin=db.Column(db.String(128), nullable=False)
    timestamp =db.Column(db.String(128), nullable=False)
    message =db.Column(db.String(256), nullable=False)
        

@app.route('/')
def index():
    stations = Data.query.all()
    return render_template('index.html',stations = stations)

@app.route('/create', methods=['GET','POST'])
def create():
    if request.method == "GET":
        return render_template('create.html')
 
    if request.method == "POST":
        vin =  request.form['vin']
        manufacturer =  request.form['manufacturer']
        model =  request.form['model']
        owner =  request.form['owner']
        fid= request.form['fid']
        reg_status =  request.form['reg_status']
 
        station_data = Data(vin, manufacturer, model,owner, fid,reg_status)
        db.session.add(station_data)
        db.session.commit()

        with open('management.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([vin, manufacturer, model, owner, fid, reg_status])
 
        return redirect(url_for('index'))

@app.route('/update/<string:vin>', methods=['GET','POST'])
def update(vin):
    station_data = Data.query.filter_by(vin=vin).first()
    if request.method == "POST":
        original_vin = vin
        
        station_data.vin =  request.form['vin']
        station_data.manufacturer =  request.form['manufacturer']
        station_data.model =  request.form['model']
        station_data.owner =  request.form['owner']
        station_data.fid= request.form['fid']
        station_data.reg_status =  request.form['reg_status']

        db.session.commit()

        lines = []
        with open('management.csv', 'r') as readFile:
            reader = csv.reader(readFile)
            for row in reader:
                if len(row) > 0 and row[0] == original_vin:
                    row[0] = request.form['vin']
                    row[1] = request.form['manufacturer']
                    row[2] = request.form['model']
                    row[3] = request.form['owner']
                    row[4] = request.form['fid']
                    row[5] = request.form['reg_status']
                lines.append(row)
        
        with open('management.csv', 'w', newline='') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(lines)

        return redirect(url_for('index'))
    return render_template('update.html', station = station_data)
 
@app.route('/delete/<string:vin>', methods = ['GET', 'POST'])
def delete(vin):
    station_data = Data.query.filter_by(vin=vin).first()
    db.session.delete(station_data)
    db.session.commit()

    lines = list()
    with open('management.csv', 'r') as readFile:
        reader = csv.reader(readFile)
        for row in reader:
            lines.append(row)
            if row[0] == vin:
                lines.remove(row)
    
    with open('management.csv', 'w', newline='') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(lines)

    return redirect(url_for('index'))

@app.route("/upload", methods=['POST'])
def uploadFiles():
    if request.method == 'POST':
        csv_file = request.files['file']
        csv_file = TextIOWrapper(csv_file, encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
        
        with open('management.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            for row in csv_reader:
                stations = Data(vin=row[0], manufacturer=row[1], model=row[2], owner=row[3],fid=row[4], reg_status=row[5])
                db.session.add(stations)
                db.session.commit()
                writer.writerow(row)

    return redirect(url_for('index'))

@app.route('/csv_report')
def download_csv():
    result = db.session.execute("SELECT vin,manufacturer,model,owner,fid,reg_status FROM stations")

    output = io.StringIO()
    writer = csv.writer(output)

    for row in result:
        line = [row[0] ,row[1], row[2],row[3]]
        writer.writerow(line)

    output.seek(0)
    db.session.commit()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=transit-station-report.csv"})



@app.route('/telemetry', methods=['POST'])
def add_telemetry():
    data = request.get_json()
    new_telemetry = Telemetry(
        vin=data['vin'],
        timestamp=data['timestamp'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        battery=data['battery'],
        odometer=data['odometer']
    )
    db.session.add(new_telemetry)
    db.session.commit()
    return jsonify({'message': 'Telemetry data added successfully'})

@app.route('/telemetry/<string:vin>', methods=['GET'])
def get_telemetry(vin):
    telemetry_data = Telemetry.query.filter_by(vin=vin).all()
    if not telemetry_data:
        return jsonify({'error':'No telemetry data found for this VIN'})
    
    ans=[]
    for data in telemetry_data:
        ans.append({
            'vin': data.vin,
            'timestamp': data.timestamp,
            'latitude': data.latitude,
            'longitude': data.longitude,
            'battery': data.battery,
            'odometer': data.odometer
        })
    return jsonify({'telemetry_data': output})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
