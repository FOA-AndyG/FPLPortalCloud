// Call the dataTables jQuery plugin
$(document).ready(function() {
    $('table.main_table').DataTable({
        order: [0, "desc"],
        lengthMenu: [[ 5, 20, 50, -1], [ '5', '20', '50', 'Show all' ]],
    });

    $('table.no_sort_table').DataTable({
        "order": [],
        "lengthMenu": [[ 5, 20, 50, -1], [ '5', '20', '50', 'Show all' ]],
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