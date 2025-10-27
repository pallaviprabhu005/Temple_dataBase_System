from flask import Flask, render_template, request, redirect
import sqlite3
import os.path
import shortuuid

currentdirectory = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(currentdirectory, "counter.db")

app = Flask(__name__) #flask initialise

#Flask routes decide which function runs for each page or action.

#Route 1--->Loads the homepage (main.html) which contains a form
@app.route("/")
def main():
    return render_template("main.html")

#Route 2--->Form submission-entering all data requeired and storing it in db
#Reads data from the form (request.form).
#Generates a unique receipt number using shortuuid.
@app.route("/", methods=["POST"])
def counter():
    if request.method == "POST":

        details = request.form
        dat = details["date"]
        nam = details["name"]
        amt = int(details["totalhidden"])
        gon = []
        gon.append(int(details["manga_count"]))
        gon.append(int(details["maha_count"]))
        gon.append(int(details["ashlesha_count"]))
        gon.append(int(details["karpura_count"]))
        gon.append(int(details["sarpa_count"]))
        gon.append(int(details["abhi_count"]))

        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            Did = str(shortuuid.uuid())

            query1 = "INSERT INTO Data VALUES('{Date}','{Name}','{Did}')".format(
                Date=dat, Name=nam, Did=Did)
            cursor.execute(query1)
            connection.commit()

            query2 = "INSERT INTO AMT VALUES({Amount},'{RN}')".format(
                Amount=amt, RN=Did)
            cursor.execute(query2)
            connection.commit()

            for i, pooja in enumerate(gon):
                if pooja != 0:
                    query2 = "INSERT INTO maintable(Recieptno,Count,Poojaid) VALUES('{Recieptno}',{Count},{Poojaid})".format(
                        Recieptno=Did, Count=pooja, Poojaid=i)
                    cursor.execute(query2)
                    connection.commit()
            cursor.close()
            return redirect("/") #after saving data, ur redirected to homepage
    else:
        return render_template("main.html")

#Route 3 —--> Users page
#Connects to the database.
#Fetches all user records by joining: data,main-table,types of seva
# And also calculates the total amount and Passes results to users.html for display
@app.route("/users")
def users():
    with sqlite3.connect(db_path) as connection:
        cur = connection.cursor()
        cur.execute("SELECT Did,Date,Name,Count,Pooja FROM Data,maintable,typesofseeva WHERE Data.Did = maintable.Recieptno AND maintable.Poojaid = typesofseeva.Id")
        details = cur.fetchall()
        cur.execute("SELECT SUM(Amount) FROM AMT")
        tamt = str(cur.fetchone()[0])+" Rs"

        obj = {
            "details": details,
            "tamount": tamt,
        }

        return render_template("users.html", obj=obj)

#Route 4 —--> List page
#Uses list.html to show all entries (with amount) and all related details.
@app.route("/list")
def list():
    with sqlite3.connect(db_path) as connection:
        cur = connection.cursor()
        cur.execute("SELECT Did,Date,Name,Count,Pooja,Amount FROM Data,maintable,typesofseeva,AMT WHERE Data.Did = maintable.Recieptno AND maintable.Poojaid = typesofseeva.Id AND Data.Did = AMT.RN")
        details = cur.fetchall()
        cur.execute("SELECT SUM(Amount) FROM AMT")
        tamt = str(cur.fetchone()[0])+" Rs"

        obj = {
            "details": details,
            "tamount": tamt,
        }

        return render_template("list.html", obj=obj)

#Route 5 —--> Search by name
#Activated when the search form on users.html is submitted.
#Searches by Name and Returns matching records.
@app.route("/users", methods=["POST"])
def search():
    try:
        if request.method == "POST":
            name = request.form["name"]
            yesname = bool(name)
            if yesname:
                with sqlite3.connect(db_path) as connection:
                    cu = connection.cursor()
                    cu.execute(
                        "SELECT Did, Date, Name, Count, Pooja FROM Data, maintable, typesofseeva WHERE Data.Did=maintable.Recieptno AND maintable.Poojaid=typesofseeva.Id AND Name LIKE '%{n}%'".format(
                            n=name))
                    details = cu.fetchall()
                    return render_template("users.html", here=details)
            else:
                return "PLEASE ENTER VALUE!!"
    except:
        return "SORRY!! NO SUCH DATA AVAILABLE !!"

#Route 6 —--> Search by date
#Activated when searching by Date.
#Filters records by the date pattern and displays results.
@ app.route("/date", methods=["POST"])
def search1():
    try:
        if request.method == "POST":
            date = request.form["date"]
            yesdate = bool(date)
            if yesdate:
                with sqlite3.connect(db_path) as connection:
                    cu = connection.cursor()
                    cu.execute(
                        "SELECT Did, Date, Name, Count, Pooja,Amount FROM Data, maintable, typesofseeva,AMT WHERE Data.Did=maintable.Recieptno AND maintable.Poojaid=typesofseeva.Id AND Data.Did=AMT.RN AND Date LIKE '%{d}%'".format(d=date))
                    datedata = cu.fetchall()
                    return render_template("users.html", there=datedata)
            else:
                return "PLEASE ENTER VALUE!!"
    except:
        return "SORRY!! NO SUCH DATA AVAILABLE !!!"

#Starts the Flask web server in debug mode
if __name__ == "__main__":
    app.run(debug=True)

