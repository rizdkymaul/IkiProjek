from flask import Flask, render_template, request, redirect, make_response, flash
from  myFunction import *
from xhtml2pdf import pisa  
import matplotlib
import os

matplotlib.use('agg')

app = Flask(__name__)
app.secret_key = 'secret key'

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/proses", methods=['GET', 'POST'])
def proses():
    if request.method == 'POST':
        minSup = request.form.get('support')
        minConf = request.form.get('confidence')
        lift = request.form.get('lift')
        startDate = request.form.get('startDate')
        endDate = request.form.get('endDate')

        if 'file' not in request.files:
            flash('No file part in the request')
            return redirect('/')
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect('/')

        file.save('./dataset/' + file.filename)

        if(checkStartDate(file.filename, startDate) == 'kurang'):
            flash('Periode tanggal awal kurang dari dataset tersimpan. Masukan sesuai dengan awal periode dataset!')
            return redirect('/')
        if(checkStartDate(file.filename, startDate) == 'lebih'):
            flash('Periode tanggal awal lebih dari dataset tersimpan. Masukan sesuai dengan awal periode dataset!')
            return redirect('/')

        if(checkEndDate(file.filename, endDate) == 'kurang'):
            flash('Periode tanggal akhir kurang dari dataset tersimpan. Masukan sesuai dengan akhir periode dataset!!')
            return redirect('/')
        if(checkEndDate(file.filename, endDate) == 'lebih'):
            flash('Periode tanggal akhir lebih dari dataset tersimpan. Masukan sesuai dengan akhir periode dataset!!')
            return redirect('/')
        
        if(startDate > endDate):
            flash('Periode Tidak Valid. Masukan periode tanggal akhir tidak kurang dari periode tanggal awal')
            return redirect('/')


        data = prosesData(minSup, minConf, file.filename, startDate, endDate)
        if(data == False):
            flash('Result is empty!')
            return redirect('/')
        liftFilter = lift5(file.filename, minSup, minConf, lift)
        terjualPenjualan = terjual_penjualan(file.filename, startDate, endDate)
        lists = plotPenjualan(file.filename)
        html =  render_template("hasil.html", table=data, liftFilter = liftFilter, terjual = terjualPenjualan[0], penjualan=terjualPenjualan[1], list = lists, lift = lift)

        pdf = pisa.CreatePDF(html, dest=None)

        if not pdf.err:
            response = make_response(pdf.dest.getvalue())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename=output.pdf'

            return response

        return 'Error while generating PDF'
    else:
        return redirect('/')
