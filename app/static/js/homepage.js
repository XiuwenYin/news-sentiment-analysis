
// 等页面加载完成后执行
document.addEventListener('DOMContentLoaded', function () {
    // 找到所有 dropdown
    var dropdowns = document.querySelectorAll('.dropdown');

    dropdowns.forEach(function (dropdown) {
        dropdown.addEventListener('mouseover', function () {
            let toggle = dropdown.querySelector('[data-bs-toggle="dropdown"]');
            if (toggle) {
                let dropdownInstance = bootstrap.Dropdown.getOrCreateInstance(toggle);
                dropdownInstance.show();
            }
        });

        dropdown.addEventListener('mouseleave', function () {
            let toggle = dropdown.querySelector('[data-bs-toggle="dropdown"]');
            if (toggle) {
                let dropdownInstance = bootstrap.Dropdown.getOrCreateInstance(toggle);
                dropdownInstance.hide();
            }
        });
    });
});

