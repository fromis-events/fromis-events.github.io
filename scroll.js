async function scroll_top()
{
    let last_height = 0
    let max_height = 0
    window.scroll_finished = false

    // keep trying to scroll every 500ms
    let handle = setInterval(function()
    {
        window.scrollBy({
		    top: window.scrollY + 1500,
            behavior: "smooth"
		});
    }, 10000);

    // if the scroll height hasn't changed for 10s, we are done
    while (true)
    {
        last_height = window.scrollY


//        await new Promise(resolve => setTimeout(resolve, 120000));
        await new Promise(resolve => setTimeout(resolve, 50000));

        if (window.scrollY === last_height)
        {
            clearInterval(handle);
            window.scroll_finished = true
            return Promise.resolve("Finished")
        }
    }
}
scroll_top()
