$(document).ready(function() {
    $('form').on('submit', function(event) {
        // get the form data
        var formData = {
            'from_name': $('input[id=from_name]').val(),
            'from_city': $('input[id=from_city]').val(),
            'from_state': $('input[id=from_state]').val(),
            'to_name': $('input[id=to_name]').val(),
            'to_city': $('input[id=to_city]').val(),
            'to_state': $('input[id=to_state]').val(),
        };

        // process the form
        $.ajax({
            type: 'GET',
            url: 'separations',
            data: formData,
            dataType: 'json',
            encode: true,
            success: function(response) {
                // convert an enum to display strings, since it is unclear if splitting the string would be better
                var typeToMessage = {
                    'person_location': ['Person', 'Location'],
                    'location_person': ['Location', 'Person'],
                    'phone_person': ['Phone', 'Person'],
                    'person_phone': ['Person', 'Phone'],
                    'person_person': ['Person', 'Person']
                };

                var responseData = [];
                var arrayLength = response.results.length;
                for (var i = 0; i < arrayLength; i++) {
                    var nextResult = response.results[i];
                    responseData.push({
                        'from_type': typeToMessage[nextResult.type][0],
                        'from_entity': nextResult.connections[0],
                        'to_type': typeToMessage[nextResult.type][1],
                        'to_entity': nextResult.connections[1],
                        'is_historical': (nextResult.is_historical ? 'Yes' : 'No')
                    });
                }

                $('#results').bootstrapTable({
                    columns: [
                    {
                        field: 'from_type',
                        title: 'From Type'
                    }, {
                        field: 'from_entity',
                        title: 'From'
                    }, {
                        field: 'to_type',
                        title: 'To Type'
                    }, {
                        field: 'to_entity',
                        title: 'To'
                    }, {
                        field: 'is_historical',
                        title: 'Is Historical?'
                    }]
                });
                $('#results').bootstrapTable('load', responseData);
                $('#results').show();
                $('#errors').hide();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                var message;
                var detail = null;
                if (jqXHR.status) {
                    // message
                    var statusMessages = {
                        '400': 'Invalid search parameters. All inputs are required.',
                        '404': 'Invalid search request. This should not happen! Please let us know what you did.',
                        '422': 'Search failed.',
                        '500': 'The service is temporarily unavailable.',
                        '503': 'The service is temporarily unavailable.'
                    };
                    message = statusMessages[jqXHR.status];

                    // detail
                    // TODO put the input validation errors next to the corresponding form elements
                    if (jqXHR.responseText) {
                        var response = jQuery.parseJSON(jqXHR.responseText);
                        var status = response.status;
                        if (status == 'input_errors') {
                            detail = '';
                            var fromErrors = response.from_errors;
                            var fromLength = fromErrors.length;
                            if (fromLength > 0) {
                                detail += '"From" search terms are invalid:<br/>'
                                for (var i = 0; i < fromLength; i++) {
                                    detail += (fromErrors[i] + '<br/>');
                                }
                            }
                            var toErrors = response.to_errors;
                            var toLength = toErrors.length;
                            if (toLength > 0) {
                                detail += '"To" search terms are invalid:<br/>'
                                for (var i = 0; i < toLength; i++) {
                                    detail += (toErrors[i] + '<br/>');
                                }
                            }
                        }
                        else if (status == 'no_from_endpoints') {
                            detail = 'The given "From" search terms yielded no results.';
                        }
                        else if (status == 'no_to_endpoints') {
                            detail = 'The given "To" search terms yielded no results.';
                        }
                        else if (status == 'no_endpoints') {
                            detail = 'The given "From" and "To" search terms yielded no results.';
                        }
                    }
                }
                else {
                    // covers parseerror, timeout, abort, etc.
                    message = 'Search failed. Please try again.'
                }

                $('#results').hide();

                $('#error-message').html(message);
                $('#error-detail').html(detail);
                $('#errors').show();
            }
        });

        event.preventDefault();
    });
});