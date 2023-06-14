$(document).ready(function () {
    // contect Form ajaxify
    var contectForm = $(".contect-form")
    var contectFormMethod = contectForm.attr("method")
    var contectFormEndPoint = contectForm.attr("action")


    function dispaySubmitting(sbmitBtn, DefaultText, doSubmit) {
        if (doSubmit) {
            sbmitBtn.addClass("disabled")
            sbmitBtn.html("<i class='fa fa-spin fa-spinner'></i>Sending...")
        } else {
            sbmitBtn.removeClass("disabled")
            sbmitBtn.html(DefaultText)
        }
    }

    contectForm.submit(function (event) {
        event.preventDefault()
        var contectFormSubmitBtn = contectForm.find("[type='submit']")
        var contectFormSubmitBtntxt = contectFormSubmitBtn.text()

        var contectFormData = contectForm.serialize()
        var thisForm = $(this)
        dispaySubmitting(contectFormSubmitBtn, "", true)
        $.ajax({
            method: contectFormMethod,
            url: contectFormEndPoint,
            data: contectFormData,
            success: function (data) {
                contectForm[0].reset()
                $.alert({
                    title: "Success!",
                    content: data.message,
                    theme: "modern",
                })
                setTimeout(function () {
                    dispaySubmitting(contectFormSubmitBtn, contectFormSubmitBtntxt, false)
                }, 500)
            },
            error: function (errorData) {
                console.log(errorData.responseJSON)
                var jsonData = errorData.responseJSON
                var msg = ""

                $.each(jsonData, function (key, value) {
                    msg += key + ":" + value[0].message + "<br>"
                })

                $.alert({
                    title: "Oops!",
                    content: msg,
                    theme: "modern",
                })
                setTimeout(function () {
                    dispaySubmitting(contectFormSubmitBtn, contectFormSubmitBtntxt, false)
                }, 500)
            }
        })
    })




    // Auto search
    var searchForm = $(".serach-form")
    var searchInput = searchForm.find("[name='q']")
    var typingTimer;
    var typingInterval = 500
    var searchBtn = searchForm.find("[type='submit']")

    searchInput.keyup(function (event) {
        //key released
        clearTimeout(typingTimer)
        typingTimer = setTimeout(performSearch, typingInterval)
    })

    searchInput.keydown(function (event) {
        //key prashed
        clearTimeout(typingTimer)
    })

    function dispaySearching() {
        searchBtn.addClass("disabled")
        searchBtn.html("<i class='fa fa-spin fa-spinner'></i>Searching...")
    }

    function performSearch() {
        dispaySearching()
        var query = searchInput.val()
        setTimeout(function () {
            window.location.href = '/search/?q=' + query
        }, 1000)
    }



    // cart and PRoducts logic
    var productForm = $(".form_product_ajax")

    productForm.submit(function (event) {
        event.preventDefault();
        //console.log("form is not sending")
        var thisForm = $(this)
        // var actionEndpoint = thisForm.attr("action");
        var actionEndpoint = thisForm.attr("data-endpoint");
        var httpMethod = thisForm.attr("method");
        var formData = thisForm.serialize();
        // console.log(thisForm)

        $.ajax({
            url: actionEndpoint,
            method: httpMethod,
            data: formData,
            success: function (data) {
                console.log("success")
                console.log(data)
                console.log("added", data.added)
                console.log("removed", data.removed)
                var submitSpan = thisForm.find(".submit-span")
                if (data.added) {
                    submitSpan.html("In cart <button type='submit' class='btn btn-link'>Remove?</button>")
                } else {
                    submitSpan.html("<button class='btn btn-success'>Add to cart</button>")
                }
                var navbarCount = $(".navbar-cart-count")
                navbarCount.text(data.cartItemsCount)
                var currentPath = window.location.href

                if (currentPath.indexOf("cart") != -1) {
                    refreshCart()
                }
            },
            error: function (errorData) {
                $.alert({
                    title: "Oops!",
                    content: "An error occurred",
                    theme: "modern",
                })
            }
        })


        function refreshCart() {
            console.log("in current cart")
            var cartTable = $(".cart-table")
            var cartBody = cartTable.find(".cart-body")
            // cartBody.html("<h1>Changed</h1>")
            var productRows = cartBody.find(".cart-product")
            var currentUrl = window.location.href

            var refreshCartUrl = '/api/cart/'
            var refreshCartMethod = "GET";
            var data = {};
            $.ajax({
                url: refreshCartUrl,
                method: refreshCartMethod,
                data: data,

                success: function (data) {

                    var hiddenCartItemRemoveForm = $(".cart-item-remove-form")
                    if (data.products.length > 0) {
                        productRows.html(" ")
                        i = data.products.length
                        $.each(data.products, function (index, value) {
                            console.log(value)
                            var newCartItemRemove = hiddenCartItemRemoveForm.clone()
                            newCartItemRemove.css("display", "block")

                            newCartItemRemove.find(".cart-item-product-id").val(value.id)
                            cartBody.prepend("<tr><th scope=\"row\">" + i + "</th><td><a href='" + value.url + "'>" + value.name + "</a>" + newCartItemRemove.html() + "</td><td>" + value.price + "</td></tr>")
                            i--
                        })
                        cartBody.find(".cart-subtotal").text(data.subtotal)
                        cartBody.find(".cart-total").text(data.total)
                    } else {
                        window.location.href = currentUrl
                    }
                },
                error: function (errorData) {
                    $.alert({
                        title: "Oops!",
                        content: "An error occurred",
                        theme: "modern",
                    })
                }
            })

        }

    })
})