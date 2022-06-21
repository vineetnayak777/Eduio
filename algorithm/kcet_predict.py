import pandas as pd

eduio_df = pd.read_csv("data/Eduio_Data.csv")

def kcet_prediction(Rank, Category):

    extracted_df = eduio_df.loc[eduio_df.Category == Category]

    less_than_rank = extracted_df.loc[extracted_df.Cutoff > Rank]

    sorted_df = less_than_rank.sort_values(by = ['Cutoff'], ascending = True)

    required_df = sorted_df[['Branch', 'College Code', 'College', 'Location']]
    
    return required_df

def kcet_prediction_yes_or_no(Rank, Category, College):

    extracted_df = eduio_df.loc[eduio_df.College == College]

    state_df = extracted_df.loc[extracted_df.Cutoff>Rank]

    state_df_category = state_df.loc[state_df.Category == Category]

    sorted_df = state_df_category.sort_values(by = ['Cutoff'], ascending= True)

    if(state_df_category.empty):
        return "no"

    return sorted_df[['Branch', 'College Code', 'College', 'Location']]

def kcet_prediction_yes_or_no_both(Rank, Category, College, Branch):
    extracted_df = eduio_df.loc[eduio_df.College == College]

    branch_df = extracted_df.loc[extracted_df.Branch == Branch]

    category_df = branch_df.loc[branch_df.Category == Category]

    cutoff_check_df = category_df.loc[category_df.Cutoff > Rank]

    if(cutoff_check_df.empty):
        return "not"

    return "possibly"

def kcet_prediction_wrt_city(Rank, Category, Location):
    extracted_df = eduio_df.loc[eduio_df.Category == Category]

    less_than_rank = extracted_df.loc[extracted_df.Cutoff > Rank]

    df_by_location = less_than_rank.loc[less_than_rank.Location == Location]

    sorted_df = df_by_location.sort_values(by = ['Cutoff'], ascending = True)

    return sorted_df[['Branch', 'College Code', 'College', 'Location']]

def kcet_prediction_wrt_branch(Rank, Category, Branch):
    extracted_df = eduio_df.loc[eduio_df.Branch == Branch]

    less_than_rank = extracted_df.loc[extracted_df.Cutoff > Rank]

    df_by_branch = less_than_rank.loc[less_than_rank.Category == Category]

    sorted_df = df_by_branch.sort_values(by = ['Cutoff'], ascending = True)

    return sorted_df[['Branch', 'College Code', 'College', 'Location']]
