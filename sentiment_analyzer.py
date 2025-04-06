import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import os
import re

# Download required NLTK data (only needed first time)
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

def clean_text(text):
    """
    Clean the review text by:
    1. Removing URLs
    2. Removing special characters and numbers
    3. Converting to lowercase
    4. Removing extra whitespace
    """
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove special characters and numbers
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text

def analyze_sentiment(text, star_rating):
    """
    Analyze the sentiment of a given text using VADER sentiment analysis.
    Incorporates the star rating into the final score.
    Returns a score between 0 (most negative) and 1 (most positive).
    """
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(text)
    
    # Convert star rating to a 0-1 scale (assuming 5-star scale)
    star_score = float(star_rating.split()[0]) / 5.0
    
    # Combine VADER score and star rating
    # Weight star rating more heavily (70%) than VADER score (30%)
    vader_score = (sentiment_scores['compound'] + 1) / 2
    combined_score = (0.4 * star_score) + (0.6 * vader_score)
    
    return combined_score

def add_sentiment_scores(input_file, output_file=None):
    """
    Read the CSV file, clean the data, add sentiment scores, and save to a new file.
    """
    # Read the CSV file
    print(f"Reading data from {input_file}...")
    df = pd.read_csv(input_file)
    
    # Clean the review text
    print("Cleaning review text...")
    df['Cleaned Review'] = df['Review Body'].apply(clean_text)
    
    # Remove rows with empty reviews after cleaning
    df = df[df['Cleaned Review'].str.len() > 0]
    
    # Add sentiment scores
    print("Analyzing sentiment of reviews...")
    df['Positivity Score'] = df.apply(lambda row: analyze_sentiment(row['Cleaned Review'], row['Rating']), axis=1)
    
    # If no output file specified, create one with '_with_sentiment' suffix
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_with_sentiment.csv"
    
    # Save to new CSV file
    df.to_csv(output_file, index=False)
    print(f"Analysis complete! Results saved to {output_file}")
    
    # Print some statistics
    print("\nSentiment Analysis Statistics:")
    print(f"Number of reviews analyzed: {len(df)}")
    print(f"Average Positivity Score: {df['Positivity Score'].mean():.3f}")
    print(f"Most Positive Review Score: {df['Positivity Score'].max():.3f}")
    print(f"Most Negative Review Score: {df['Positivity Score'].min():.3f}")
    
    # Print distribution of scores
    print("\nScore Distribution:")
    print(df['Positivity Score'].describe())
    
    # Print average score by star rating
    print("\nAverage Positivity Score by Star Rating:")
    print(df.groupby('Rating')['Positivity Score'].mean().sort_index())

if __name__ == "__main__":
    # You can modify these file paths as needed
    input_file = "MelaniaFourStars.csv"  # Replace with your input CSV file name
    add_sentiment_scores(input_file) 