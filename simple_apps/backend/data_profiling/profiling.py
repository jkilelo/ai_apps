async def get_metadata(database:str,table:str, columns:list=None)-> dict:
    """
    Get metadata of a database table.
    
    Args:
        database (str): The name of the database.
        btable (str): The name of the table.
        columns (str, optional): Comma-separated list of columns to retrieve. If None, retrieves all columns.
        
    Returns:
        dict: Metadata of the specified table.
    """

    return {
        "database": database,
        "table": table,
        "columns": columns if columns else None,
    }