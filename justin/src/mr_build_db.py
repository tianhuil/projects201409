# mr_build_db.py

# Uses map reduce to try to parallelize building the SQL database of trip times grouped
# by starting/ending coordinates, day, and hour. The data are currently hosted in 168
# separate files. The "mapping" phase should involve sending these jobs

