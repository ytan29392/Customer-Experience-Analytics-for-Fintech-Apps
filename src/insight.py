import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from datetime import datetime

# --- Visualization Functions ---

def plot_sentiment_distribution(df: pd.DataFrame, output_dir: Path):
    """Bar plot of sentiment distribution by bank."""
    plt.figure(figsize=(12, 6))
    ax = sns.countplot(
        data=df,
        x='bank',
        hue='sentiment_label',
        palette={'positive': '#4CAF50', 'neutral': '#FFC107', 'negative': '#F44336'},
        order=df['bank'].value_counts().index
    )
    plt.title("Customer Sentiment Distribution by Bank", fontsize=14, pad=20)
    plt.xlabel("Bank", fontsize=12)
    plt.ylabel("Number of Reviews", fontsize=12)
    plt.legend(title='Sentiment', bbox_to_anchor=(1.05, 1))

    for p in ax.patches:
        height = p.get_height()
        ax.text(p.get_x() + p.get_width()/2., height + 3,
                f'{height/len(df)*100:.1f}%', ha="center", fontsize=10)

    plt.tight_layout()
    plt.savefig(output_dir / "sentiment_distribution.png", dpi=300)
    plt.close()

def plot_rating_vs_sentiment(df: pd.DataFrame, output_dir: Path):
    """Violin plot of sentiment scores by star rating."""
    plt.figure(figsize=(12, 6))
    sns.violinplot(
        data=df,
        x='rating',
        y='sentiment_score',
        palette='RdYlGn',
        inner='quartile'
    )
    plt.title("Sentiment Scores Distribution by Star Rating", fontsize=14, pad=20)
    plt.xlabel("Star Rating (1-5)", fontsize=12)
    plt.ylabel("Sentiment Score", fontsize=12)
    plt.axhline(0, color='black', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_dir / "rating_vs_sentiment.png", dpi=300)
    plt.close()

def generate_wordclouds(df: pd.DataFrame, output_dir: Path):
    """Generate word clouds for each bank's reviews."""
    for bank in df['bank'].unique():
        text = ' '.join(df[df['bank'] == bank]['review'])
        wordcloud = WordCloud(
            width=1200,
            height=600,
            background_color='white',
            colormap='viridis',
            max_words=200
        ).generate(text)

        plt.figure(figsize=(12, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.title(f"Frequent Words in {bank} Reviews", fontsize=14, pad=20)
        plt.axis('off')
        plt.savefig(output_dir / f"wordcloud_{bank[:3].lower()}.png", dpi=300, bbox_inches='tight')
        plt.close()

# --- Insight Generation ---

def generate_insights(df: pd.DataFrame) -> dict:
    """Extract key insights from analyzed data."""
    insights = {
        'banks': {},
        'comparisons': {
            'avg_sentiment': df.groupby('bank')['sentiment_score'].mean().round(3).to_dict()
        }
    }

    for bank in df['bank'].unique():
        bank_data = df[df['bank'] == bank]
        pos_reviews = bank_data[bank_data['sentiment_label'] == 'positive']
        neg_reviews = bank_data[bank_data['sentiment_label'] == 'negative']

        insights['banks'][bank] = {
            'pos_percentage': f"{len(pos_reviews)/len(bank_data)*100:.1f}%",
            'top_pos_keywords': pos_reviews['keywords'].explode().value_counts().head(3).index.tolist(),
            'top_neg_keywords': neg_reviews['keywords'].explode().value_counts().head(3).index.tolist()
        }

    return insights

# --- Markdown Report ---

def generate_report(insights: dict, output_dir: Path):
    """Generate markdown report with insights and visualizations."""
    report = f"""# Fintech App Reviews Analysis Report
Date: {datetime.now().strftime('%Y-%m-%d')}

## Key Insights

### 1. Overall Sentiment Distribution
![Sentiment Distribution](sentiment_distribution.png)

### 2. Bank Performance Comparison
| Bank | Avg. Sentiment | % Positive | Top Positive Keywords | Top Negative Keywords |
|------|----------------|------------|------------------------|------------------------|"""

    for bank, data in insights['banks'].items():
        report += f"""
| {bank[:20]} | {insights['comparisons']['avg_sentiment'][bank]} | {data['pos_percentage']} | {', '.join(data['top_pos_keywords'])} | {', '.join(data['top_neg_keywords'])} |"""

    report += """

### 3. Detailed Analysis
![Rating vs Sentiment](rating_vs_sentiment.png)

## Recommendations
1. Improve Login Experience: Address 'login' issues mentioned in negative reviews
2. Enhance Performance: Optimize for keywords like 'slow' and 'lag'
3. Feature Development: Prioritize features mentioned in positive reviews
"""

    with open(output_dir / "report.md", "w") as f:
        f.write(report)
