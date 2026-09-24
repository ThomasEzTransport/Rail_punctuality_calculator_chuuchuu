# Domestic ICE trains:
ICE_germany_mask = (
    (data_chuuchuu["routeType"]=="ICE") 
    & (data_chuuchuu["journey_type"] == "domestic") 
    & (data_chuuchuu["country"]=="Germany")
    & (data_chuuchuu["operator"].isna())
    )

data_chuuchuu.loc[ICE_germany_mask, "operator"] = "DB"

# International ICE trains

ICE_dict = {"Germany" : "DB",
            "Switzerland" : "SBB",
            "Austria": "OEBB",
            "Belgium": "SNCB",
            "Netherlands": "NS",
            "France": "SNCF"}

ICE_international_mask =(
    (data_chuuchuu["routeType"]=="ICE") 
    & (data_chuuchuu["journey_type"] == "international") 
    & (data_chuuchuu["operator"].isna())
    )

# We consider that international ICE trains are joint services with other operators in arriving/departing country
endpoint_countries_by_journey = (
    data_chuuchuu.loc[data_chuuchuu["depart_terminus"].isin(["depart", "terminus"])]
    .groupby("journey_id")["country"]
    .agg(lambda countries: set(countries.dropna()))
)

def _db_joint_operator(countries):
    if "Germany" not in countries:
        return np.nan
    other_countries = countries - {"Germany"}
    if len(other_countries) != 1:
        return np.nan
    (other_country,) = other_countries
    other_agency = ICE_dict.get(other_country)
    if other_agency is None:
        return np.nan
    return f"DB/{other_agency}"

db_joint_operator_by_journey = endpoint_countries_by_journey.apply(_db_joint_operator)
resolved_operator = data_chuuchuu["journey_id"].map(db_joint_operator_by_journey)

data_chuuchuu.loc[ICE_international_mask, "operator"] = resolved_operator[ICE_international_mask]

n_resolved = (ICE_international_mask & resolved_operator.notna()).sum()
print(f"{n_resolved} / {ICE_international_mask.sum()} international ICE rows resolved to a DB/<agency> operator")
print(data_chuuchuu.loc[ICE_international_mask, "operator"].value_counts(dropna=False))