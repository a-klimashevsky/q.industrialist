﻿<?php
include 'qi_render_html.php';
include_once '.settings.php';
?>

<?php function __dump_monthly_jobs() {
    if (!extension_loaded('pgsql')) return;
    $conn = pg_connect("host=".DB_HOST." port=".DB_PORT." dbname=".DB_DATABASE." user=".DB_USERNAME." password=".DB_PASSWORD)
            or die('pg_connect err: '.pg_last_error());
    pg_exec($conn, "SET search_path TO qi");
    $query = 'SELECT wmj_id,wmj_active,wmj_quantity,wmj_eft,wmj_remarks FROM workflow_monthly_jobs ORDER BY 4;';
    $jobs_cursor = pg_query($conn, $query)
            or die('pg_query err: '.pg_last_error());
    $jobs = pg_fetch_all($jobs_cursor);
    pg_close($conn);
    $jobs_sz = sizeof($jobs);
?>
<nav class="navbar navbar-default">
 <div class="container-fluid">
  <div class="navbar-header">
   <button type="button" class="collapsed navbar-toggle" data-toggle="collapse"
    data-target="#bs-jobs-navbar-collapse" aria-expanded="false">
   <span class="sr-only">Toggle navigation</span>
   <span class="icon-bar"></span>
   <span class="icon-bar"></span>
   <span class="icon-bar"></span>
   </button>
   <a data-target="#" class="navbar-brand">Scheduling</a>
  </div>
  <div class="collapse navbar-collapse" id="bs-jobs-navbar-collapse">
   <button type="button" class="btn btn-default navbar-btn" id="qind-btn-add">Add new</button>
  </div>
 </div>
</nav> 
<div class="panel-group" id="monthly_jobs" role="tablist" aria-multiselectable="true">
<?php
    // вывод информации о корабле, а также формирование элементов пользовательского интерфейса
    foreach ($jobs as &$job)
    {
        $id = $job['wmj_id'];
        $q = $job['wmj_quantity'];
        $cmnt = $job['wmj_remarks'];
        $fit = $job['wmj_eft'];
        $nm = substr(strtok(strtok($fit, "\n"), ","), 1);
?>
<div class="panel panel-default">
 <div class="panel-heading" role="tab" id="monthjob_hd<?=$id?>">
  <h4 class="panel-title">
   <a role="button" data-toggle="collapse"
    href="#monthjob_collapse<?=$id?>" aria-expanded="true"
    aria-controls="monthjob_collapse<?=$id?>"><strong><?=$nm?></strong>&nbsp;<span
    class="badge" id="qind-job-q<?=$id?>"><?=$q?></span></a>
  </h4>
  <span id="qind-job-rmrks<?=$id?>"><?=$cmnt?></span>
 </div>
 <div id="monthjob_collapse<?=$id?>" class="panel-collapse collapse"
  role="tabpanel" aria-labelledby="monthjob_hd<?=$id?>">
  <div class="panel-body">
   <div class="row">
    <div class="col-md-6">
     <button type="button" class="btn btn-default btn-xs disabled"><span
      class="glyphicon glyphicon-eye-close" aria-hidden="true"></span>&nbsp;<span>T2</span></button>
     <button type="button" class="btn btn-default btn-xs qind-btn-eft" data-toggle="modal"
      data-target="#modalEFT<?=$id?>"><span class="glyphicon glyphicon-th-list"
      aria-hidden="true"></span>&nbsp;EFT</button>
    </div>
    <div class="col-md-4 col-md-offset-2" align="right">
     <button type="button" class="btn btn-default btn-xs qind-btn-edit" job="<?=$id?>" ship="<?=$nm?>"><span
      class="glyphicon glyphicon-pencil" aria-hidden="true"></span></button>
     <button type="button" class="btn btn-default btn-xs disabled"><span class="glyphicon
      glyphicon-cloud" aria-hidden="true"></span></button>
     <button type="button" class="btn btn-default btn-xs qind-btn-del" job="<?=$id?>"><span class="glyphicon
      glyphicon-trash" aria-hidden="true"></span></button>
    </div>
   </div>
   <hr style="margin-top: 6px; margin-bottom: 10px;">
   <pre class="pre-scrollable" style="border: 0; background-color: transparent; font-size: 11px;"
    id="qind-job-eft<?=$id?>"><?=$fit?></pre></div>
 </div>
</div>
<?php
        // добавление окна, в котором можно просматривать и копировать EFT
        __dump_any_into_modal_header_wo_button(
            sprintf('<strong>%sx %s</strong>%s',
                    $q,
                    $nm,
                    !is_null($cmnt) && !empty($cmnt) ? '<small><br>'.$cmnt.'</small>' : ''
            ),
            'EFT'.$id, // modal добавляется автоматически
            NULL // 'modal-sm'
        );
        // формируем содержимое модального диалога
        echo '<textarea onclick="this.select();" class="col-md-12" rows="15" style="resize:none"'.
             ' readonly="readonly">'.$fit.'</textarea>';
        // закрываем footer модального диалога
        __dump_any_into_modal_footer();
    }
    unset($job);
?>
</div>
<form class="hidden" action="qi_digger.php" method="get" id="frmDelFit">
 <input type="hidden" name="module" value="workflow">
 <input type="hidden" name="action" value="del">
 <input type="hidden" name="fit" value="2">
</form>
<script>
$(document).ready(function(){
  $('button.qind-btn-del').each(function(){
    $(this).on('click', function () {
      var frm = $("#frmDelFit");
      frm.find("input[name='fit']").val($(this).attr('job'));
      frm.submit();
    })
  })
})
</script>

<div class="modal fade" id="modalFit" tabindex="-1" role="dialog" aria-labelledby="modalFitLabel">
 <div class="modal-dialog" role="document">
  <div class="modal-content">
   <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
    <h4 class="modal-title" id="modalFitLabel"></h4>
   </div>
   <div class="modal-body">
    <form action="qi_digger.php" method="post" id="frmEditFit">
     <input type="hidden" name="module" value="workflow">
     <input type="hidden" name="action" value="edit">
     <input type="hidden" name="fit" value="0">
     <div class="form-group">
      <label for="eft">EFT</label>
      <textarea class="form-control" id="eft" name="eft" rows="15" style="resize:none; font-size: 11px;" spellcheck="false"></textarea>
     </div>
     <div class="form-group">
      <label for="quantity">Quantity</label>
      <input type="number" class="form-control" id="quantity" name="quantity" min="1" max="100000">
     </div>
     <div class="form-group">
      <label for="remarks">Remarks</label>
      <input class="form-control" id="remarks" name="remarks" value="" maxlength="127">
     </div>
    </form>
   </div>
   <div class="modal-footer">
    <button type="submit" class="btn btn-primary" onclick="$('#frmEditFit').submit();">Save</button>
    <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
   </div>
  </div>
 </div>
</div>
<script>
$(document).ready(function(){
  $('button.qind-btn-edit').each(function(){
    $(this).on('click', function () {
      var job = $(this).attr('job');
      var ship = $(this).attr('ship');
      var q = $("#qind-job-q"+job).text();
      var rmrks = $('#qind-job-rmrks'+job).text();
      var eft = $('#qind-job-eft'+job).html();
      var modal = $("#modalFit");
      $('#modalFitLabel').html(q + 'x ' + ship);
      modal.find('textarea').html(eft);
      modal.find("input[name='remarks']").val(rmrks);
      modal.find("input[name='quantity']").val(q);
      modal.find("input[name='fit']").val(job);
      modal.find("input[name='action']").val('edit');
      modal.modal('show');
      frm.submit();
    })
  })
  $('#qind-btn-add').on('click', function () {
      var modal = $("#modalFit");
      $('#modalFitLabel').html('Scheduling new monthly job...');
      modal.find('textarea').html('');
      modal.find("input[name='remarks']").val('');
      modal.find("input[name='quantity']").val(1);
      modal.find("input[name='fit']").val(0);
      modal.find("input[name='action']").val('add');
      modal.modal('show');
      frm.submit();
  })
})
</script>
<?php } ?>


<?php __dump_header("Workflow Settings", true); ?>
<div class="container-fluid">
 <div class="row">
  <div class="col-md-6">
   <h3>Monthly Scheduled Jobs</h3>
   <?php __dump_monthly_jobs(); ?>
  </div>
  <div class="col-md-6">
   <h3>Containers</h3>
   &times; &times; &times; &times; &times;
  </div>
 </div> <!--row-->
</div> <!--container-fluid-->
<?php __dump_footer(); ?>