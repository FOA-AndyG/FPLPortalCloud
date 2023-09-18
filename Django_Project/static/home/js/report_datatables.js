// Call the dataTables jQuery plugin
$(document).ready(function() {
    $('table.report_table').DataTable({
        dom: 'Bfrtip',
        order: [],
        buttons: [
            {extend:'pageLength', className: 'btn btn-default'},
            {extend:'excel', autoFilter: true, className: 'btn btn-info', sheetName: 'Sheet1',
             exportOptions:{columns: ':visible:not(.notexport)'},
             text: 'Export Table'},
        ]
    });

    $('table.main_table').DataTable({
        dom: 'Bfrtip',
        order: [],
        buttons: [
            {extend:'pageLength', className: 'btn btn-default'},
            {extend:'excel', autoFilter: true, className: 'btn btn-info', sheetName: 'Sheet1',
             exportOptions:{columns: ':visible:not(.notexport)'},
             text: 'Export Table'},
        ]
    });

    $('table.scan_table').DataTable({
        dom: 'Bfrtip',
        order: [],
        buttons: [
            {extend:'pageLength', className: 'btn btn-default'},
            {
                extend:'excel', autoFilter: true, className: 'btn btn-info', sheetName: 'Sheet1',
                exportOptions:{columns: ':visible:not(.notexport)'},
                text: 'Export Table',
                customizeData: function(data) {
                    for(var i = 0; i < data.body.length; i++) {
                        for(var j = 0; j < data.body[i].length; j++) {
                            data.body[i][j] = '\u200C' + data.body[i][j];
                        }
                    }
                },
                orientation: 'landscape'
            },
        ],
        // columnDefs: [{ "type": "html", "targets": 2 }]
    });



});

//$(document).ready(function() {
//     $('table.main_table').DataTable({
//        autoWidth: true,
//        order: [0, "asc"],
//        dom: 'Bfrtip',
//        lengthMenu: [[ 10, 20, 50, -1], [ '10 rows', '20 rows', '50 rows', 'Show all' ]],
//        buttons: [
//        {extend:'pageLength', className: 'btn btn-default'},
//        ]
//     });
//});