var STATE_URL = '/state';
var SOURCE_URL = '/source';
var SWITCHES_URL = '/switches';
var IR_URL = '/ir';
var PANDORA_URL = '/pandora';

function reloadState() {
    $.get(STATE_URL, loadState, 'json');
}

function loadState(state) {
    console.log(state);
    $.each(state.switches, function(i, state) {
        $('#room-'+i).val(state ? 'on' : 'off').slider('refresh');
        $('#room-'+i).slider({value: state?'on':'off',
            animate: false});
    });

    updateSourceSelect(state.source);
    if ('pandora' in state) {
        updatePandoraStatus(state.pandora);
    }
}

function updateSourceSelect(source) {
    $('#source-' + source).prop('checked', true);
    $('input[type=radio]').checkboxradio('refresh');

    if (source == 'Cd')
        $('.cd-control').show();
    else
        $('.cd-control').hide();

    if (source == 'Tuner')
        $('.tuner-control').show();
    else
        $('.tuner-control').hide();

    if (source == 'Usb')
        $('.usb-control').show();
    else
        $('.usb-control').hide();

    if (source == 'Pandora')
        $('.pandora-control').show();
    else
        $('.pandora-control').hide();
}

function updatePandoraStatus(pandoraStatus) {
    if (!pandoraStatus) {
        pandoraStatus = {
            'paused': true,
            'coverArt': '',
            'artist': '',
            'title': '',
            'album': '',
            'stations': {},
            'stationName': ''
        };

        $('.pandora-status').text('Not running');
    } else {
        $('.pandora-status').text(
            pandoraStatus.paused ? 'Paused': 'Playing'
        );
    }

    $('img.pandora-cover').attr('src', pandoraStatus.coverArt);
    $('.pandora-artist').text(pandoraStatus.artist);
    $('.pandora-title').text(pandoraStatus.title);
    $('.pandora-album').text(pandoraStatus.album);

    var $stations = $('select.pandora-stations');
    $.each(pandoraStatus.stations, function(id, name) {
        $stations.append(
            $('<option />').val(id).text(name)
            .attr('selected', name == pandoraStatus.stationName)
        );
    });
    $stations.selectmenu('refresh', true);
}

$(window).bind('pageshow', function(event) {
    console.log('pageshow');
    reloadState();
});

$(function() {
    $('[id^=room-]').change(function() {
        var room = this.id.split('-')[1];
        var val = ($(this).val() == 'on') ? 1 : 0;
        console.log(room, val);

        $.post(SWITCHES_URL, {room: room, val: val},
            loadState, 'json');
    });

    $('button[data-ir]').click(function() {
        var ir = $(this).data('ir');
        console.log('IrButton', ir);

        $.post(IR_URL, {ir: ir}, loadState, 'json');
    });

    $('button[data-pandora]').click(function() {
        var cmd = $(this).data('pandora');
        console.log('PandoraButton', cmd);

        $.post(PANDORA_URL, {cmd: cmd}, loadState, 'json');
    });

    $('[id^=source-]').click(function() {
        var source = this.id.split('-')[1];

        console.log('SrcButton', source);
        updateSourceSelect(source);
        $.post(SOURCE_URL, {source: source}, loadState, 'json');
    });

    $('.pandora-stations').change(function() {
        $.post(PANDORA_URL, {cmd: 'select_station', arg: $(this).val()});
    });

    $('.reload-button').click(reloadState);

    setInterval(reloadState, 5000);
});
