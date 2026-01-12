<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Document</title>
	<link rel="stylesheet" href="./css/style.css">
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">
</head>
<body>
	
<!-- include navbar -->
<?php include 'components/navbar.php'; ?>
<!----- inner header section ------>
<section class="partners-header-section">
    <div class="container text-center py-5">
        <h1 class="text-white fw-bold mb-2">Accommodation</h1>
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb justify-content-center mb-0">
                <li class="breadcrumb-item"><a href="#" class="text-white text-decoration-none">HOME</a></li>
                <li class="breadcrumb-item active text-orange" aria-current="page">ACCOMMODATION</li>
            </ol>
        </nav>
    </div>
</section>

<!---- hero map seciton ---->
<?php include 'components/map_section.php'; ?>



<section class="explore-section py-5 bg-white">
    <div class="container py-4">
        <div class="row justify-content-center text-center">
            <div class="col-lg-8">
                <h2 class="section-title mb-4">
                    Accommodation <span class="text-orange">Listings</span>
                </h2>
                <p class="section-subtitle text-muted px-md-5">
                    At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis
                </p>
            </div>
        </div>
    </div>
</section>


<!-------- card------>
<?php include 'components/card.php'; ?>





<!---------- footer section ---------->
<?php include 'components/footer.php'; ?>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js" integrity="sha384-FKyoEForCGlyvwx9Hj09JcYn3nv7wiPVlz7YYwJrWVcXK/BmnVDxM+D2scQbITxI" crossorigin="anonymous"></script>	
</body>
</html>