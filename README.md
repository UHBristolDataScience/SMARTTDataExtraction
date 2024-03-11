# SMARTTDataExtraction
Data extraction and processing for SMARTT.

This repository will provide a detailed recipe, along with accompanying scripts, for extraction and processing of the data required by the SMARTT project from ICCA. It should be sufficiently prescriptive that the process can be followed at any participating site to produce data in the correct format to allow federated validation of the SMARTT algorithm(s). 

Please work through the steps below in order (click on the step to expand the instructions). If at any stage you encounter a problem please send a description to [chris.mcwilliams@bristol.ac.uk](mailto:chris.mcwilliams@bristol.ac.uk?subject=bug_report) along with any associated error messages.

#### Note: currently only step 1 is implemented!

<details>

<summary>Step 1.</summary>

### Setup and installation

In this step you will setup the environment, install required packages and then run some tests to confirm that everything is working correclty. 

The system and user requirements are as follows:
* You need to have admin rights to download and install software from the internet on your machine (specifically python packages using pip and Git)

Run the following:
* python -m pip install --upgrade
* python -m pip install streamlit, streamlit-extras st-pages pyodbc openpyxl
* 

</details>

<details>

<summary>Step 2.</summary>

### Variable mapping

In this step you will map physiological variables of interest (see section [Data Description](#data-description)) to intervention and attribute IDs in the backend database of ICCA. Instructions and code to follow soon...

</details>

<details>


<summary>Data description.</summary>

# Data Description

We begin with the definition of the variables that need to be extracted from ICCA. [Our original](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6429919/) model used only 15 physiological variables in order to provide a fair test against a [set of nurse-led discharge critera](https://europepmc.org/article/med/12737189). To improve on our original model we will add more variables and also engineer additional features by processing and combining these variables in different ways, in order to improve the predictive performance. As our starting point we take the set of variables that were used in [the model published by Pacmed](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8437217/). These variables are listed in the table below and also defined in the [schema spreadsheet](https://github.com/UHBristolDataScience/SMARTTDataExtraction/blob/main/schema/smartt_variable_definitions.xlsx). Note that the `number of features' refers to the number of features that were derived from these variables for input to the model (using their feature engineering approach described [here](https://cdn-links.lww.com/permalink/ccx/a/ccx_1_1_2021_08_13_thoral_cce-d-21-00060_sdc1.pdf)).

| Feature Category	| Feature Name |	Number of Features |
| --- | --- | --- |
| **General information** | | |
| Patient characteristics	| Age, gender, and weight at admission |	3 |
| Admission information | Origin department	| 3 |
| **Laboratory results** | | |
| Blood gas analysis |	pH, Paco2, Pao2, actual bicarbonate, base excess, and arterial oxygen saturation |	15 |
| Hematology |	Hemoglobin, WBC count, platelet count, activated partial thromboplastin time, and prothrombin time |	16 |
| Routine chemistry |	Sodium, potassium, creatinine, ureum, creatinine/ureum ratio, chloride, ionized calcium, magnesium, phosphate, lactate dehydrogenase, glucose, lactate, C-reactive protein, and albumin |	43 |
| Cardiac enzymes |	Creatinine kinase and troponin-T |	5 |
| Liver and pancreas tests |	Bilirubin, alanine aminotransferase, aspartate aminotransferase, alkaline phosphatase, Gamma-glutamyltransferase, and amylase	| 11 |
| **Vital signs and device data** | | |
| Circulation |	Heart rate, arterial blood pressure (systolic/diastolic/mean), noninvasive blood pressure (systolic/diastolic), cardiac output, temperature, and central venous pressure |	34 |
| Respiration |	Fio2, positive end-expiratory pressure, tidal volume, respiratory rate, peripheral oxygen saturation, and rapid shallow breathing index	| 18 |
| **Clinical observations and scores** | | |
| Neurology |	Glasgow Coma Scale score, Richmond Agitation-Sedation Scale, pupil response, and pupil diameter |	9 |
| Respiration |	Bronchial suctioning, coughing reflex, and Pao2/Fio2 |	10 |
| Nephrology |	Urine output |	2 |
| **Diagnostics and therapeutics** | | | 
| Lines, drains and tubes |	Endotracheal tube and urine catheter |	3 |
| Interventions |	Supplemental oxygen, continuous renal replacement therapy, and tube feeding |	8 |
| Total	 |	180 |


</details>
