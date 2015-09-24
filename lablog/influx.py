POLICIES = [
{
    "name": "\"realtime\"",
    "duration": "1d",
    "replication": 1,
    "default":True,
},
{
    "name": "\"15minute\"",
    "duration": "4w",
    "replication": 1,
    "default": False,
},
{
    "name": "\"1hour\"",
    "duration": "INF",
    "replication": 1,
    "default": False,
}
]

QUERIES = [
    {
        "name":"15_minute_rollup",
        "query":"SELECT mean(\"value\") as value INTO \"{database}\".\"15minute\".:measurement FROM \"{database}\".\"realtime\"./^[a-z]+.*/ GROUP BY time(15m), *"
    },
    {
        "name":"1_hour_rollup",
        "query":"SELECT mean(\"value\") as value INTO \"{database}\".\"1hour\".:measurement FROM \"{database}\".\"realtime\"./^[a-z]+.*/ GROUP BY time(1h), *"
    }
]
