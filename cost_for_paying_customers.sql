SELECT
    SUM(cost) AS cost,
    cost_category
FROM
    aws_cost_report
WHERE
    start_date >= {start_date}
    AND start_date < {end_date}
    AND account_uuid IN (
        'acc_gVe9NjHiQiul5D0kJuOdhg',
        'acc_JLkQkqwHTuaFW9sqf-r-xQ',
        'acc_PcIfJ9h7TymMw5nApnglYg',
        'bXrhk6dXQCiZbzYNNVxjuw',
        'MS2X5aDrRm-yaHgnZs7g3A',
        'acc_8xdvgfppTBKCiQvUgCoLyA',
        'jntuvw96QqeVGdhjx1dmzg',
        'acc_GjAicCWBRA2DfBB0EfU4cg',
        'acc_SqsqcVb8TxKlMuWkOczb3A'
    )
GROUP BY
    cost_category