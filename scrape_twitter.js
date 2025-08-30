my_data = {}
my_data.data = []

async function scroll_top()
{
    while (true)
    {
        // if (window.location.href === "https://x.com/fromis9_japan/with_replies")
        // if (window.location.href.endsWith('&f=live'))
        if (window.location.href.endsWith('with_replies'))
        // if (window.location.href === "https://x.com/realfromis_9")
        {
            console.log("STARTING");
            break;
        }

        console.log("WAITING...");
        await new Promise(resolve => setTimeout(resolve, 10000));
    }

    let last_height = 0

    // keep trying to scroll every 500ms
    let handle = setInterval(function()
    {
        window.scrollBy({
		    top: document.body.scrollHeight,
            behavior: "smooth"
		});
    }, 5000);

    // if the scroll height hasn't changed for 10s, we are done
    while (true)
    {
        last_height = window.scrollY

        await new Promise(resolve => setTimeout(resolve, 120000));

        if (window.scrollY === last_height)
        {
            clearInterval(handle);
            return Promise.resolve("Finished")
        }
    }
}

scroll_top()

function hook2() {
    const originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function (method, url) {
        this.addEventListener("load", function () {
            if (url.includes('UserTweetsAndReplies?'))
            // if (!url.includes('UserTweets?'))
            {
                let requestData = {
                    type: "XHR",
                    method: method,
                    url: url,
                    status: this.status,
                    response: this.responseText
                };

                let parsed = JSON.parse(this.response);
                // data.data = data.data.concat(parsed['data']['user']['result']['timeline_v2']['instructions'][0]['entries']);
                let instructions = parsed['data']['user']['result']['timeline_v2']['timeline']['instructions']
                for (let i of instructions)
                {
                    if (i['type'] === 'TimelineAddEntries')
                    {
                        let entries = i['entries']
                        my_data.data = my_data.data.concat(entries);
                        console.log(entries.length, my_data.data.length);
                    }
                }
            }
            else if (url.includes('SearchTimeline?'))
            {
                let parsed = JSON.parse(this.response);
                let instructions = parsed['data']['search_by_raw_query']['search_timeline']['timeline']['instructions']
                for (let i of instructions)
                {
                    if (i['type'] === 'TimelineAddEntries')
                    {
                        let entries = i['entries']
                        my_data.data = my_data.data.concat(entries);
                        console.log('SearchTimeline', entries.length, my_data.data.length);
                    }
                }
            }

            // console.log(entries);
            // console.log(parsed);
            // console.log(requestData);
        });
        return originalOpen.apply(this, arguments);
    };
}

function hook3() {
    const originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function (method, url) {
        this.addEventListener("load", function () {
            if (url.includes('SearchTimeline?'))
            {
                let parsed = JSON.parse(this.response);
                let instructions = parsed['data']['search_by_raw_query']['search_timeline']['timeline']['instructions']
                for (let i of instructions)
                {
                    if (i['type'] === 'TimelineAddEntries')
                    {
                        let entries = i['entries']
                        my_data.data = my_data.data.concat(entries);
                        console.log('SearchTimeline', entries.length, my_data.data.length);
                        window.my_data = my_data.data
                    }
                }
            }

            // console.log(entries);
            // console.log(parsed);
            // console.log(requestData);
        });
        return originalOpen.apply(this, arguments);
    };
}

function remove_hook()
{
    XMLHttpRequest.prototype.open = XMLHttpRequest.prototype.nativeOpen;
}

function download_json(data)
{
    const jsonData = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonData], {type: "application/json"});
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'twitter.json';
    link.click();
}

async function main()
{
    // setup_hook()
    // hook2()
    hook3();

    // let replies_button = document.getElementsByClassName('css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-b88u0q r-1awozwy r-6koalj r-18u37iz r-1pi2tsx r-1777fci r-1l7z4oj r-95jzfe r-bnwqim')[0]
    // replies_button.click();
    // await new Promise(resolve => setTimeout(resolve, 2000));

    await scroll_top();

    download_json(my_data.data);
    // remove_hook();
    alert('Finished')
    return Promise.resolve();
}

await main()