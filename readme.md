### Getting Started :

1. First Setup a virtual environment and install dependencies using this command :
```powershell
python -m venv venv
pip install -r requirements.txt
```

2. Create a .env file to store env variables (APIs).


### runing the app (local):
#### FrontEnd :
```Powershell
streamlit run .\frontend\main.py
```

#### Backend :
```Powershell
python -m uvicorn app.main:app --reload
```

> make sure to do this before in the terminal:
```Powershell
$env:PYTHONPATH = "."                          
```

### testing queries :
1. Under IFRS, what criteria must be met for an asset to be recognized on the statement of financial position?
2. How does IFRS define control for the purposes of consolidating a subsidiary?
3. How does IFRS treat subsequent measurement of investment property?
4. How is taxable profit determined for corporate income tax purposes in Tunisia?
5. How is VAT treated on exports and international services?
