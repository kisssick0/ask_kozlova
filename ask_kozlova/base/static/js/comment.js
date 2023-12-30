//var correctable_answers = document.getElementsByClassName('correct-section')

//console.log(correctable_answers);

    const container = document.getElementById('counter');

    const centrifuge = new Centrifuge("{{ centrifugo.ws_url }}", {
      token: "{{ centrifugo.token }}"
    });

    centrifuge.on('connecting', function (ctx) {
      console.log(`connecting: ${ctx.code}, ${ctx.reason}`);
    }).on('connected', function (ctx) {
      console.log(`connected over ${ctx.transport}`);
    }).on('disconnected', function (ctx) {
      console.log(`disconnected: ${ctx.code}, ${ctx.reason}`);
    }).connect();

    const sub = centrifuge.newSubscription("{{ centrifugo.channel }}");

    sub.on('publication', function (ctx) {
      console.log(ctx);
    }).on('subscribing', function (ctx) {
      console.log(`subscribing: ${ctx.code}, ${ctx.reason}`);
    }).on('subscribed', function (ctx) {
      console.log('subscribed', ctx);
    }).on('unsubscribed', function (ctx) {
      console.log(`unsubscribed: ${ctx.code}, ${ctx.reason}`);
    }).subscribe();