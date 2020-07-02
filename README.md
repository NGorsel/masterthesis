# masterthesis

This repository contains all code used in the master thesis of Niels van Gorsel. An overview of all files:


## data_pipeline folder
A data pipeline  written in Python. The main file is created in such a way that the user only needs to give the script an Instagram account. The code automatically srapes all followers, creates a sample size of the followers and obtains all posts created in 2019 of this sample size. All posts are stored as a .cvs file in the data folder. The name of the company follower profile is : data/rawprofiles/COMPANYNAME_followerProfile.csv. The main.py file uses a wide variety of HTTP requests which are imported from the API_calls.py file. The lasy samplesize.py is used to compute a sample size for a given population size.

## notebook folder
This folder contains in total 8 different jupyter notebooks. Each notebook contains a variety of functions used to process the raw company follower profiles created with the data_pipeline. A small explanation for each notebook is provided below:

2. postCleaning.ipynb - Takes as input one specific company follower profile. It cleans the content of the posts by removing stopwords, punctuation. Futhermore, it detects hashtags and user mentions within the text of a posts and stores this as a seperate column. Once the company follower profile is cleaned it is stored as a pickle file in the following directory: "data/cleanedprofiles/COMPANYNAME_cleaned.pkl"

3. removeOutliers.ipynb - Takes as input all the cleaned follower profiles from the data/cleanedprofiles folder. It caclulates the number of times each follower posted. By doing so it is able to remove all followers who posted > 2.5x MAD + Median. Furthermore, it computes the number of times each hashtag is used by a follower. By doing so it is able to remove all hashtags which are only used by one specific user. This is required to reduce the number of dimensions in the vector space. Once these hashtags and users are identifies it loops through all company follower profiles and removes these hashtags and users from the dataset. The output is stored as a pickle file in the following  directory. data/noNoise/COMPANYNAME_cleaned_noNoise.pkl

4. Create vector spaces.ipynb - Here the collection of company follower profiles are transformed into a vector space model. A wide variety of functions enable maximum user easability. The user only has to provide the follower attributes: data_input (hashtag, text, combined), post_level (absolute, relative), user_level (absolute, relative), IDF_penalty (yes/no). Based on the provided attributes all cleaned follower profiles without noise are transformed into a vector space model which is stored as a pickle file the following directory: vector_spaces/vector_hashtag_Pabsolute_Uabsolute.pkl. Please note that the filename indicates which settings were used.

5. Calculate Distance between companies.ipynb - This notebook uses a distance metric (cosine similarity, Jaccard similarity or Euclidean distance) to calculate a distance between each pair of companies. It uses a vector space created in chapter 4, stored in the vector-space folder, as input. The distance matrix is stored in the following folder: results/hashtag_cosine_Pabsolute_Uabsolute_TFIDF.pkl. Finally, it is able to visualise the distnance matrix using the Seaborn library.

6. Evaluation Methods.ipynb - This notebook fist starts by importing the  SBI and Interview gold standards. After this a wide variety of code is created to compute a precision, recall and f1-score for the distance matrix when compared to one of the two gold standards. The best performing threshold is discovered by using both  n-fold cross validation and by looping through all thresholds of 0.001 to 1.0. The notebook also computes a baseline model for both gold standard and compares performance of SBI standard with respect to Interview gold standard. Lastly, it contains a code used to compute the sector distinguish metric for a specific distance matrix.

* The last two notebooks are not used in the research. However, they are used to create visuals which may help the used to obtain a better understanding of the distance matrix which is created.\

7. Cluster similarity scores.ipynb [EXTRA] - A variety of cluster algorithms can be used on  the distance matrix to see how the distance matrix would group the companies together based on their  similarity score. The user can choose between: Spectral clustering, Kmeans and DBSCAN.

8. Is used to transform the distance matrix into a static network visualization. The nodes of the network represent the companies, the distance between the companies represent their similarity distance which is computed by 1 - similarity score. Only the edges are drawn between companies showing a similarity above a certain threshold which is provided by the user.

## gold standards
Contains a CSV file containing all 90 companies used in the analysis. For each of the 90 companies it shows all index codes of the Dutch Chamber of Commerce for each of the 90 companies. The Interview gold standard is just hard-coded in the evaluation notebook by manually creating a dictionary.


If you have any questions about the code placed in this repository you can always contact me on my personal mail adres: niels.v.gorsel@gmail.com. Thank you!