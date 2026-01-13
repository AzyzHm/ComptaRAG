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
1. Under IFRS, what conditions must be met to recognize a provision, and how does this differ from contingent liabilities? (IFRS)

2. Comment est déterminé le résultat fiscal à partir du résultat comptable selon la législation tunisienne ? (Fiscalité tunisienne)

3. How does IFRS 15 allocate the transaction price in a contract with multiple performance obligations? (IFRS)

4. Comment la TVA est-elle traitée sur les exportations de biens et les services internationaux en Tunisie ? (Fiscalité tunisienne)

5. How should a USD-denominated trade receivable be remeasured at year-end under IAS 21? (IFRS / Foreign currency)

6. Une provision comptabilisée selon IAS 37 mais non déductible fiscalement en Tunisie : quel est l’impact en matière d’impôt différé ? (IFRS / Fiscalité tunisienne)

7. How does IFRS define control for the purpose of consolidating a subsidiary? (IFRS)

8. Quelles charges sont considérées comme non déductibles fiscalement en Tunisie ? (Fiscalité tunisienne)

9. What is the difference between a change in accounting policy and a change in accounting estimate under IFRS? (IFRS)

10. Une entreprise tunisienne facture en euros : comment les écarts de change sont-ils traités comptablement et fiscalement ? (IFRS / Fiscalité tunisienne)

11. How are financial assets classified and measured under IFRS 9? (IFRS)

12. Comment est calculé l’impôt sur les sociétés en Tunisie pour une société résidente ? (Fiscalité tunisienne)

13. What is the current EUR/TND exchange rate, and how would it affect the valuation of foreign currency balances? (Live exchange rates)

14. Une subvention d’investissement reçue par une entreprise tunisienne : traitement comptable IFRS et traitement fiscal ? (IFRS / Fiscalité tunisienne)

15. How does IFRS treat the subsequent measurement of investment property under IAS 40? (IFRS)

16. Comment sont traitées fiscalement les provisions pour risques et charges en Tunisie ? (Fiscalité tunisienne)

17. If the Tunisian dinar depreciates after the reporting date, is this an adjusting or non-adjusting event under IFRS? (IFRS / Events after reporting period)

18. Une facture fournisseur en devise est réglée après la clôture : quel est le traitement comptable selon IAS 21 ? (IFRS / Foreign currency)

19. How is VAT applied to imported goods in Tunisia? (Fiscalité tunisienne)

20. Under IFRS 16, how is a lease liability initially measured? (IFRS)

21. Une entreprise applique les IFRS mais est soumise à la loi fiscale tunisienne : que faire en cas de divergence entre les deux ? (IFRS / Fiscalité tunisienne)

22. How are deferred tax assets recognized under IAS 12, and what evidence is required? (IFRS)

23. Comment sont imposés les revenus de source étrangère pour une société tunisienne ? (Fiscalité tunisienne)

24. How do exchange rate fluctuations impact profit or loss under IFRS? (IFRS / Foreign currency)

25. Une entreprise tunisienne exportatrice réalise des ventes exonérées de TVA : quel est l’impact sur le droit à déduction ? (Fiscalité tunisienne)
