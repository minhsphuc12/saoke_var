import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from transformers import pipeline

# Load the NER pipeline
ner_pipeline = pipeline("ner", model="NlpHUST/ner-vietnamese-electra-base")

def clean_description(description: str) -> str:
    copy_description = description
    for char in copy_description:
        if char.isdigit() or not char.isalpha():
            copy_description = copy_description.replace(char, ' ')
            
    copy_description = copy_description.strip()
    cleaned_description = ''.join(char for char in copy_description if char.isalpha() or char.isspace())
    cleaned_description = ' '.join(cleaned_description.split())  # Remove extra spaces
    return cleaned_description
    

def extract_entity_name(description: str) -> str:
    """
    Extract the first entity name (organization or person) from the given description.

    Args:
        description (str): The text description to extract entities from.

    Returns:
        str: The first extracted entity name, or an empty string if no entities are found.
    """

    # If the cleaned description is empty, return an empty string
    if not description:
        return ""
    
    # Process the cleaned description with the NER pipeline
    ner_results = ner_pipeline(description)
    parsed_entities = []
    for entity in ner_results:
        if (entity['entity'].startswith('B-') or entity['entity'].startswith('I-')) and entity['word'] not in parsed_entities:
            parsed_entities.append(entity['word'])
            # print(entity['word'])
    return ' '.join(parsed_entities) if parsed_entities else ""


def clean_entity_name(entity_name: str) -> str:
    # Remove '##' and the preceding space if present
    cleaned_name = entity_name.replace(' ##', '')
    # cleaned_name = entity_name.replace('##', '')
    return cleaned_name.strip()
import multiprocessing as mp
from functools import partial

def process_chunk(chunk, description_column):
    chunk['entity_name'] = chunk[description_column].apply(extract_entity_name)
    chunk['entity_name'] = chunk['entity_name'].apply(clean_entity_name)
    return chunk

def extract_names(input_df: pd.DataFrame, description_column: str) -> pd.DataFrame:
    """
    Extract entity names from the input DataFrame and return the results as a DataFrame.

    Args:
        input_df (pd.DataFrame): The input DataFrame to process.
        description_column (str): The name of the column containing descriptions.

    Returns:
        pd.DataFrame: The input DataFrame with an additional 'entity_name' column.
    """
    
    # Determine the number of CPU cores to use
    num_cores = mp.cpu_count()
    
    # Split the DataFrame into chunks
    chunks = np.array_split(input_df, num_cores)
    
    # Create a pool of worker processes
    pool = mp.Pool(num_cores)
    
    # Process chunks in parallel
    func = partial(process_chunk, description_column=description_column)
    results = pool.map(func, chunks)
    
    # Combine the results
    result_df = pd.concat(results)
    
    print("Extraction complete.")
    return result_df


if __name__ == "__main__":
    input_df = pd.read_csv("data.csv").head(1000)
    output_file = "data_with_entities.csv"
    description_column = "description"
    import time
    start_time = time.time()
    result_df = extract_names(input_df, description_column)
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
    
    # Save the result to a CSV file
    result_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")
