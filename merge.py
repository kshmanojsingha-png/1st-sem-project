import pandas as pd

print("1. Loading data...")
reviews = pd.read_csv('Reviews.csv')
products = pd.read_csv('amazon_products.csv', usecols=['asin', 'title'])

print("2. Cleaning IDs (removing spaces and making uppercase)...")
# Clean IDs in both files to ensure exact matching
reviews['ProductId'] = reviews['ProductId'].astype(str).str.strip().str.upper()
products['asin'] = products['asin'].astype(str).str.strip().str.upper()

print("3. Merging datasets...")
merged = pd.merge(reviews, products, left_on='ProductId', right_on='asin', how='left')

print("4. Fixing missing names...")
# If the title (name) is not found, use the Summary as the product name
merged['title'] = merged['title'].fillna(merged['Summary'])
# If the Summary is also empty, only then use 'Unknown Product'
merged['title'] = merged['title'].fillna('Unknown Product')

# Drop the extra column
merged.drop(columns=['asin'], inplace=True)

print("5. Saving new file...")
# Save the first 50,000 rows
merged.head(50000).to_csv('final_food_reviews.csv', index=False)

print("✅ Done! Product names will now be visible in the app.")