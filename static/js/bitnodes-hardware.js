/*
 * Copyright (c) Addy Yeow Chin Heng <ayeowch@gmail.com>
 * Licensed under MIT (https://github.com/ayeowch/hardware/blob/master/LICENSE)
 */

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function format(value) {
    if (value !== null)
        return value;
    else
        return '';
}

var node = {
    bitcoind_running: 'pending',  // Watched
    bitcoind_reachable: 'pending',  // Watched
    system_shutdown: false
};
var prevBlocks;
var currBlocks;
var nodeStatusTimeout = 15000;
var errors = 0;
$(function() {
    (function nodeStatus() {
        $.ajax({
            url: '/api/v1/node-status/',
            contentType: 'application/json',
            success: function(data) {
                node.bitcoind_running = data.bitcoind_running;
                if (node.bitcoind_running) {
                    $('.bitcoind_running').html('RUNNING');
                    $('.bitcoind_running').removeClass('label-default label-danger').addClass('label-success');
                } else {
                    $('.bitcoind_running').html('STOPPED');
                    $('.bitcoind_running').removeClass('label-default label-success').addClass('label-danger');
                }
                $('.lan-address').html(format(data.lan_address));
                $('.wan-address').html(format(data.wan_address));
                $('.port').html(format(data.port));
                $('.user-agent').html(format(data.user_agent));
                $('.protocol-version').html(format(data.protocol_version));
                currBlocks = data.blocks;
                $('.blocks').html(format(currBlocks));
                $('.connections').html(format(data.connections));

                if (data.connections) {
                    if (data.connections <= 8) {
                        node.bitcoind_reachable = false;
                    } else {
                        node.bitcoind_reachable = true;
                        $('.wan-address').html('<a href="https://getaddr.bitnodes.io/nodes/' + data.wan_address + '-' + data.port + '/" target="_blank" title="Node status on Bitnodes">' + format(data.wan_address) + ' <i class="fa fa-external-link"></i></a>');
                    }
                }
            },
            error: function(jqXHR) {
                if (!node.system_shutdown) {
                    errors += 1;
                    console.log('errors=' + errors);
                    if (errors >= 3) {
                        $('#overlay').fadeIn(200, 'linear', function() {
                            $('#overlay > .message').html('Error while fetching node status. Try reloading this page.');
                        });
                    }
                } else {
                    console.log(node.system_shutdown);
                }
            },
            complete: function(jqXHR) {
                if (jqXHR.statusText === 'error') {
                    if (errors >= 3)
                        return;
                } else {
                    errors = 0;
                }
                if (currBlocks === prevBlocks)
                    nodeStatusTimeout *= 1.2;
                else
                    nodeStatusTimeout = 15000;
                setTimeout(nodeStatus, nodeStatusTimeout);  // >= 15 seconds
                prevBlocks = currBlocks;
            }
        });
    })();
});

if (!Object.prototype.watch) {
    Object.defineProperty(Object.prototype, 'watch', {
        enumerable: false,
        configurable: true,
        writable: false,
        value: function(prop, handler) {
            var oldVal = this[prop],
                getter = function() {
                    return oldVal;
                },
                setter = function(newVal) {
                    if (oldVal !== newVal) {
                        handler.call(this, prop, oldVal, newVal);
                        oldVal = newVal;
                    } else {
                        return false;
                    }
                };
            if (delete this[prop]) {
                Object.defineProperty(this, prop, {
                    get: getter,
                    set: setter,
                    enumerable: true,
                    configurable: true
                });
            }
        }
    });
}

if (!Object.prototype.unwatch) {
    Object.defineProperty(Object.prototype, 'unwatch', {
        enumerable: false,
        configurable: true,
        writable: false,
        value: function(prop) {
            var val = this[prop];
            delete this[prop];
            this[prop] = val;
        }
    });
}
