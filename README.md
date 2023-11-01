# DCM_network_analysis_repo
The code for, and TensorFlow network contained in, the paper "Can Co-Authorship Networks be used to Predict Research Impact? A Machine-Learning based analysis of Degenerative Cervical Myelopathy Research"

4 scripts were used to generate the data in the article. 
- "paper_analyser.py" was used to pull the relevant information from the papers and authors using the Scopus database (as pybliometrics is only available in python). The database itself of papers is "papers.csv". Author data is generated (saved to "Python_authors_prolific.csv"), as well as coauthorship links (saved to "Python_links_prolific").
- "graphing.Rmd" was used to create the network visualisation (as VisNetwork is developed for R), and to generate further author data (using the 2 csv files generated by the python scipt above). This is saved in "author_stats.csv"
- "TF_learning.py" was used to create the neural network, as well as some basic visualisations of learning and error for the paper, all of which are automatically saved. TF_learning refers to the fact that TensorFlow was used for this (a number of other methods were tried, but the TensorFlow network proved best). The generated neural network was saved in "saved_model", and all diagrams are saved in "figs", with printouts in "readouts&stats"
- "network_testing.py" contains the scipt used to generate the diagrams in the "network sensitivities" section. A dedicated script was made for this as I couldn't find a tool that already existed to perform such visualisation, so I had to make one, and I didn't want to extend TF_learning.py any more

A brief commentary is present in all these scripts to explain the overall structure and functions of each section, but precise explainations are not present. Inefficiencies are likely to be present in the code. For any queries, or help using the code for simmilar projects, email noahgrodzinski@gmail.com 

# Changes made by me

- [ ] paper_extractor.py
- [ ] new network structure