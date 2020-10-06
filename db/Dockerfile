FROM mongo

COPY expressions.json /expressions.json
# populate expressions collection
CMD mongoimport --host mongodb --db nopla --collection expressions --type json --file /expressions.json --jsonArray