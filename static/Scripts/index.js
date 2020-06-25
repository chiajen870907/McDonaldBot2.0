var userId = "";
var displayName = "";
var pictureUrl = "";

function initializeLiff(myLiffId) {
    liff
        .init({
            liffId: myLiffId,
        })
        .then(() => {
            initializeApp();
            registerButtonHandlers();

        })
        .catch(err => {
            console.log(err);
        });
}

function initializeApp() {
    // check if the user is logged in/out, and disable inappropriate button
    if (!liff.isLoggedIn()) {
        liff.login();
    } else {
        liff.getProfile()
            .then(profile => {
                userId = profile.userId;
                displayName = profile.displayName;
                pictureUrl = profile.pictureUrl;

                $("#user-image").attr("src", pictureUrl);
                $('#userid').val(userId);
                $('#member-name').html(displayName+'，您好'); //赋值


                console.log(pictureUrl);
            })
            .catch(err => {
                console.log(err);
            });
    }
}

initializeLiff('1654329237-W78QE7qk');





function registerButtonHandlers() {

    //Call register
    document.getElementById('register').addEventListener('click', function() {
        $("#register_anim").css("display", "inline");
        $("#register").prop("dissable", true).css("display", "none");

        const sendData = {
            UID: userId,
            username: $("#username").val(),
            password: $("#password").val()

        };
        // console.log(sendData);
        // 請求伺服器
        $.ajax({
            url: "/api/appRegister",
            method: "post",
            dataType: "json",
            data: JSON.stringify(sendData),
            contentType: "application/json;charset=utf-8",
            success: function(data) {
                console.log(data.msg);
                if (data.msg === "success") {
                    init();
                    Swal.fire({
                        icon: 'success',
                        title: '註冊成功！',
                        text: '帳號已成功註冊！'
                    });
                    // liff.closeWindow();
                    // setTimeout(liff.closeWindow(), 1700);
                } else {
                    init();
                    Swal.fire({
                        icon: 'error',
                        title: '很抱歉！',
                        text: data.data,
                        confirmButtonText: '登入失敗，請重新登入'
                    });

                }
            },
            error: function() {
                // console.log(data);
                init();
            }
        });
    })
}



// 回到原來的樣子
function init() {
    $("#username").val('');
    $("#password").val('');
    $("#register").css("display", "inline");
    $("#register_anim").css("display", "none");

}

