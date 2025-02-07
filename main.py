from fastapi import FastAPI


app = FastAPI()

@app.get("/yarns")
async def all_yarn():
    #class(df) recieve df return df in dict
    return dict_of_df.get_all_yarn()
