# Install required packages
# Run these commands in your terminal before executing this script:
# pip install PyPDF2
# pip install tabula-py
# pip install pandas

import multiprocessing
import csv
from PyPDF2 import PdfReader, PdfWriter
from functools import partial
import tabula
import pandas as pd
import warnings
from tqdm import tqdm
import io
import os



warnings.filterwarnings("ignore", category=DeprecationWarning, module="pandas.core.indexing")


def clean_data(df):
    # Ensure the first column is of datetime type
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
    
    cleaned_data = []
    current_row = {}
    
    for _, row in df.iterrows():
        if pd.notnull(row.iloc[0]):  # If the first column (date) is not null, it's a new observation
            if current_row:  # If we have a current row, add it to cleaned_data
                cleaned_data.append(current_row)
            current_row = row.to_dict()  # Start a new row
        else:  # If the first column is null, it's a continuation of the previous observation
            for col, value in row.items():
                if pd.notnull(value):
                    if pd.isnull(current_row.get(col)):
                        current_row[col] = str(value)
                    else:
                        current_row[col] += ' ' + str(value)
    
    # Add the last row
    if current_row:
        cleaned_data.append(current_row)
    cleaned_data = pd.DataFrame(cleaned_data)
    cleaned_data.columns = ['trans_date', 'debit', 'credit', 'balance', 'description']
    cleaned_data = cleaned_data[['trans_date', 'credit', 'description']]
    return cleaned_data

def split_pdf_to_pages(pdf_path, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        pdf = PdfReader(file)
        
        # Iterate through all pages
        for page_num in range(len(pdf.pages)):
            # Create a new PDF writer object
            pdf_writer = PdfWriter()
            
            # Add the page to the writer
            pdf_writer.add_page(pdf.pages[page_num])
            
            # Generate the output filename
            output_filename = f'page_{page_num + 1}.pdf'
            output_path = os.path.join(output_folder, output_filename)
            
            # Write the page to a new PDF file
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
    
    print(f"PDF split into individual pages in folder: {output_folder}")

def read_table_from_pdf(pdf_path):
    import tabula
    
    # Read the PDF file
    table = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, silent=True)[0]
    # Remove the first 4 rows from the table
    table = table.iloc[4:]
    
    # Clean up the DataFrame
    table = table.dropna(how='all')  # Drop rows where all elements are NaN
    table = table.reset_index(drop=True)  # Reset the index
    table.columns = ['trans_date', 'debit', 'credit', 'balance', 'description']
    return table


def parse_and_clean_page(pdf_path):
    # Read table from PDF
    df = read_table_from_pdf(pdf_path)
    
    # Clean and process the data as before
    cleaned_data = clean_data(df)
    return cleaned_data

pdf_path='pages/page_2.pdf'
parse_and_clean_page(pdf_path='pages/page_3.pdf')

def parse_pdf_to_csv(pdf_folder, csv_path="data.csv", max_page=None, max_threads=12):
    # Get all PDF files in the folder
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    pdf_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))  # Sort by page number
    
    if max_page:
        pdf_files = pdf_files[:max_page]
    
    pdf_paths = [os.path.join(pdf_folder, pdf_file) for pdf_file in pdf_files]
    parse_and_clean_page(pdf_path=pdf_paths[0])
    
    
    # Use multiprocessing for parallel processing
    with multiprocessing.Pool(processes=min(max_threads, multiprocessing.cpu_count())) as pool:
        results = list(tqdm(pool.imap(parse_and_clean_page, pdf_paths), total=len(pdf_paths), desc="Parsing PDF pages"))

    # Combine all DataFrames
    all_data = pd.concat(results, ignore_index=True)

    # Write to CSV
    all_data.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"CSV file saved to {csv_path}")

if __name__ == "__main__":
    pdf_path = "danh-sach-ung-ho-1726197796019953464538.pdf"
    csv_path = "data.csv"
    pdf_folder = "pages"
    # split_pdf_to_pages('danh-sach-ung-ho-1726197796019953464538.pdf', 'pages')
    max_page=20; max_threads=12
    parse_pdf_to_csv(pdf_folder, csv_path)
else:
    # This ensures that parse_and_clean_page is defined in the global scope
    # when the script is imported as a module
    globals()['parse_and_clean_page'] = parse_and_clean_page
