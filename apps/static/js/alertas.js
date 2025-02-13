$(document).ready(function() {
    $('.resolver-alerta').click(function() {
        var alertaId = $(this).data('id');
        $.post('/imoveis/resolver_alerta/' + alertaId, function(response) {
            if(response.success) {
                location.reload();
            }
        });
    });
});
