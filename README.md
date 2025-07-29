Phase 1 prototype:

using sqlite for db storage
to populate existing data from management.csv


working endpoints:
@app.route("/upload", methods=['POST'])
@app.route('/create', methods=['GET','POST'])
@app.route('/update/<string:vin>', methods=['GET','POST'])
@app.route('/delete/<string:vin>', methods = ['GET', 'POST'])
@app.route('/csv_report')



<img width="1684" height="901" alt="image" src="https://github.com/user-attachments/assets/91c6d675-c5ec-4c96-ae36-78d3bde33d93" />

<img width="1716" height="890" alt="image" src="https://github.com/user-attachments/assets/f53091ae-125a-4c89-9520-c0ad61d0d6f7" />


<img width="1614" height="868" alt="image" src="https://github.com/user-attachments/assets/77b84af4-c821-4169-ae8d-6508044b42f5" />


added new vehicle:

<img width="1774" height="893" alt="image" src="https://github.com/user-attachments/assets/8a60ffe2-2ce2-4c2b-88ca-dc032956b60c" />


Current Status:

working on telemetry to get and add telemetry to telemetry database! (created endpoints need to check on it!)
working on alerts logic 


