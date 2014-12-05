$(function() {
    $('form[method!="GET"]').not('#filter_form').submit(function() {
        return confirm("确定操作？");
    });

    $('a.warning, a.btn.btn-large, a.btn-danger').click(function() {
       return confirm("确定操作？");
    });

    $("select[id^='filter_select_']").change(function() {
        var next_input = $(this).next();
        var name_list = next_input.attr("name").split("_");
        name_list.pop();
        name_list.push($(this).val());
        var new_name = name_list.join('_');
        next_input.attr("name", new_name);
    });

    // datetime picker l10n
    $.fn.datetimepicker.dates['cn'] = {
        days: ["周日", "周一", "周二", "周三", "周四", "周五", "周六", "周日"],
        daysShort: ["日", "一", "二", "三", "四", "五", "六", "日"],
        daysMin: ["日", "一", "二", "三", "四", "五", "六", "日"],
        months: ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
        monthsShort: ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
        today: "今天"
    };
});
