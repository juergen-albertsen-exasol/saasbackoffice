with
    mr (last_modified_at, uuid) as (
        select
            max(last_modified_at),
            uuid
        from
            clusters
        group by
            uuid
    )
select distinct
    d.account_uuid,
    d.uuid as db_uuid,
    c.uuid as cluster_uuid,
    c.name,
    c.status,
    c.last_modified_at,
    csi.tshirt_size
from
    clusters c,
    databases d,
    cluster_sizes csi,
    mr
where
    c.db_uuid = d.uuid
    and c.cluster_sizes_id = csi.id
    and d.account_uuid = 'acc_lsC4s41IR_mivzpBJ-Rx-A'
    and c.uuid = mr.uuid
    and c.last_modified_at = mr.last_modified_at
    order by account_uuid, db_uuid, cluster_uuid