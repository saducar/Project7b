import os
import sys
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from flask import Flask, render_template, request, flash

res=pd.read_csv('result.csv')

focus={'AMT_APPLICATION':'For how much credit did client ask on the previous application',
'DAYS_EMPLOYED':'How many days before the application the person started current employment',
'DAYS_BIRTH':"Client's age in days at the time of application",
'AMT_GOODS_PRICE':'Goods price of good that client asked for (if applicable) on the previous application',
'AMT_ANNUITY_x':'Annuity of previous application',
'AMT_INCOME_TOTAL':'Income of the client',
'AMT_CREDIT':' Credit amount of the loan'}


app = Flask(__name__)
app.secret_key="MeSRc9ZI9SJDei2MaTueO3PPPCHAYP2X"

IMAGES_FOLDER = os.path.join('static', 'images')
app.config['UPLOAD_FOLDER'] = IMAGES_FOLDER

def getGlobalImages():
    images=os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'global'))
    images=[os.path.join(app.config['UPLOAD_FOLDER'], 'global',img) for img in images]
    titles=['Clients with high credit amount','Portion of clients defaulting vs non-defaulting']
    dict={}
    for i in range(len(titles)):
        dict[images[i]]=titles[i]

    return dict

def getImages(id):
    res['DAYS_BIRTH']=abs(res['DAYS_BIRTH'])
    client=res[res['SK_ID_CURR']==int(id)]
    sameClass=res[res['Class']==int(client['Class'].values[0])]
    if int(client['Class'])==1:
        oppClass=res[res['Class']==0]
    else:
        oppClass=res[res['Class']==1]
    for key, val in focus.items():
        temp=pd.DataFrame(columns=['Target','Average','SameGroup','OppGroup'])
        temp['Target']=client[key]
        temp['Average']=np.average(res[key].values)
        temp['SameGroup']=np.average(sameClass[key].values)
        temp['OppGroup']=np.average(oppClass[key].values)
        temp=temp.T
        plt.figure(figsize=(8, 5))
        plt.barh(temp.index, temp[temp.columns[0]], color=plt.cm.Accent_r(np.arange(len(temp))))
        plt.savefig(os.path.join(app.config['UPLOAD_FOLDER'], 'specific', key+'.png'))
    
    images=os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'specific'))
    images=[os.path.join(app.config['UPLOAD_FOLDER'], 'specific',img) for img in images]
    
    dict={}
    for i in range(len(images)):
        key=images[i].split(os.sep)[-1]
        key=key.split('.')[0]
        dict[images[i]]=focus[key]

    return dict

@app.route("/")
def index():
    dict=getGlobalImages()
    imgs={}
    return render_template("index.html", dict=dict, imgs=imgs)

@app.route("/", methods=['POST', 'GET'])
def showResult():
    id=request.form['id_textBox']
    prob=res.loc[res['SK_ID_CURR']==int(id)]['TARGET'].values[0]*100
    flash("The client "+id+" has a "+str(round(prob, 1))+"% risk of defaulting on their loan.")
    dict=getGlobalImages()
    imgs=getImages(id)

    return render_template("index.html", dict=dict, imgs=imgs)



if __name__ == '__main__':
    app.run()