/* ========================================================================= */
/* ===== DIJKSTRA 1 TO 1 DEFINITION ======================================== */
/* ========================================================================= */

CREATE OR REPLACE FUNCTION pgr_dijkstra_random(
	edges_sql TEXT,
	noise DECIMAL,
	start_vid BIGINT,
	end_vid BIGINT,
	directed BOOLEAN,

	OUT seq integer,
	OUT path_seq integer,
	OUT node BIGINT,
	OUT edge BIGINT,
	OUT cost float,
	OUT agg_cost float
)

RETURNS SETOF RECORD AS

$$
BEGIN

DROP TABLE IF EXISTS edges_table;
DROP TABLE IF EXISTS edges_table_random;

/* Intercept the edges table that the pgr routing algorithm would normally work on, but make sure we have the geometry, too. */
EXECUTE 'CREATE TEMPORARY TABLE edges_table AS (' || edges_sql || ');';

/* Replace the cost columns with random cost */
CREATE TEMPORARY TABLE
	edges_table_random
AS (
	SELECT
		edges_table.id AS id,
		edges_table.source AS source,
		edges_table.target AS target,
		edges_table.cost + (((random() * 2) - 1) * noise * edges_table.cost) AS cost,
		edges_table.reverse_cost + (((random() * 2) - 1) * noise * edges_table.reverse_cost) AS reverse_cost
	FROM
		edges_table
);

/* Now run the pgr routing algorithm on the updated table & return the result. */
RETURN QUERY (
	SELECT
		*
	FROM
		pgr_dijkstra(
			'SELECT id, source, target, cost, reverse_cost FROM edges_table_random;',
			start_vid,
			end_vid,
			directed
		)
);

END
$$
LANGUAGE plpgsql;
