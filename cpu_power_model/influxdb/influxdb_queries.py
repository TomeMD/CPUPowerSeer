load_query = '''
    from(bucket: "{influxdb_bucket}")
        |> range(start: {start_date}, stop: {stop_date})
        |> filter(fn: (r) => r["_measurement"] == "percpu")
        |> filter(fn: (r) => r["_field"] == "user" or r["_field"] == "system")
        |> aggregateWindow(every: 2s, fn: mean, createEmpty: false)
        |> group(columns: ["_measurement"])
        |> aggregateWindow(every: 2s, fn: sum, createEmpty: false)'''

user_load_query = '''
    from(bucket: "{influxdb_bucket}")
        |> range(start: {start_date}, stop: {stop_date})
        |> filter(fn: (r) => r["_measurement"] == "percpu")
        |> filter(fn: (r) => r["_field"] == "user" )
        |> aggregateWindow(every: 2s, fn: mean, createEmpty: false)
        |> group(columns: ["_measurement"])
        |> aggregateWindow(every: 2s, fn: sum, createEmpty: false)'''

system_load_query = '''
    from(bucket: "{influxdb_bucket}")
        |> range(start: {start_date}, stop: {stop_date})
        |> filter(fn: (r) => r["_measurement"] == "percpu")
        |> filter(fn: (r) => r["_field"] == "system" )
        |> aggregateWindow(every: 2s, fn: mean, createEmpty: false)
        |> group(columns: ["_measurement"])
        |> aggregateWindow(every: 2s, fn: sum, createEmpty: false)'''

wait_load_query = '''
    from(bucket: "{influxdb_bucket}")
        |> range(start: {start_date}, stop: {stop_date})
        |> filter(fn: (r) => r["_measurement"] == "percpu")
        |> filter(fn: (r) => r["_field"] == "iowait" )
        |> aggregateWindow(every: 2s, fn: mean, createEmpty: false)
        |> group(columns: ["_measurement"])
        |> aggregateWindow(every: 2s, fn: sum, createEmpty: false)'''

freq_query = '''
    from(bucket: "{influxdb_bucket}")
        |> range(start: {start_date}, stop: {stop_date})
        |> filter(fn: (r) => r["_measurement"] == "cpu_frequency")
        |> filter(fn: (r) => r["_field"] == "average" )
        |> aggregateWindow(every: 2s, fn: mean, createEmpty: false)'''

energy_query = '''
    from(bucket: "{influxdb_bucket}")
        |> range(start: {start_date}, stop: {stop_date})
        |> filter(fn: (r) => r["_measurement"] == "ENERGY_PACKAGE")
        |> filter(fn: (r) => r["_field"] == "rapl:::PACKAGE_ENERGY:PACKAGE0(J)" or r["_field"] == "rapl:::PACKAGE_ENERGY:PACKAGE1(J)")
        |> aggregateWindow(every: 2s, fn: sum, createEmpty: false)
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> map(fn: (r) => ({{
            _time: r._time,
            host: r.host,
            _measurement: r._measurement,
            _field: "total_energy",
            _value: (if exists r["rapl:::PACKAGE_ENERGY:PACKAGE0(J)"] then r["rapl:::PACKAGE_ENERGY:PACKAGE0(J)"] else 0.0)
                  + (if exists r["rapl:::PACKAGE_ENERGY:PACKAGE1(J)"] then r["rapl:::PACKAGE_ENERGY:PACKAGE1(J)"] else 0.0)
        }}))'''

temp_query = '''
    from(bucket: "{influxdb_bucket}")
        |> range(start: {start_date}, stop: {stop_date})
        |> filter(fn: (r) => r["_measurement"] == "sensors")
        |> filter(fn: (r) => r["_field"] == "value")
        |> filter(fn: (r) => r["label"] == "Package id 0" or r["label"] == "Package id 1")
        |> aggregateWindow(every: 2s, fn: mean, createEmpty: false)
        |> pivot(rowKey:["_time"], columnKey: ["label"], valueColumn: "_value")
        |> map(fn: (r) => ({{
            _time: r._time,
            _value: (if exists r["Package id 0"] then r["Package id 0"] else 0.0) 
                  + (if exists r["Package id 1"] then r["Package id 1"] else 0.0)
        }}))
'''

var_query = {
    "load": load_query,
    "user_load": user_load_query,
    "system_load": system_load_query,
    "wait_load": wait_load_query,
    "freq": freq_query,
    "energy": energy_query,
    "temp": temp_query
}