import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Step 2: Read data from Excel
excel_file = "pokedexCEL.xlsx"  # Update with your Excel file path
df = pd.read_excel(excel_file)

# Fill missing values in 'Type2' column with 'None'
df['Type2'].fillna('None', inplace=True)

# Pivot the DataFrame to have Type1 as rows, Type2 as columns, and count as values
heatmap_data = df.groupby(['Type1', 'Type2']).size().unstack(fill_value=0)

# Reorder the columns to place 'None' at the end
column_order = heatmap_data.columns.tolist()
column_order.remove('None')
column_order.append('None')
heatmap_data = heatmap_data[column_order]

# Plot the heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_data, cmap='YlGnBu', annot=True, fmt='d', linewidths=.5)
plt.title('Distribution of Type Combinations (Including Single Types)')
plt.xlabel('Type2')
plt.ylabel('Type1')
plt.xticks(rotation=45)
plt.yticks(rotation=0)
plt.tight_layout()

# Save the heatmap to a file (replace 'heatmap.png' with your desired file path)
plt.savefig('heatmap_with_single_types_reordered.png')

# Show the plot
plt.show()
