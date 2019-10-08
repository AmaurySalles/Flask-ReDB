// Thanks to Zelenin for the basis of the code below - https://bootsnipp.com/snippets/OQ4V
// jQuery plugin method used by Zelenin https://stackoverflow.com/questions/2937227/what-does-function-jquery-mean

// jQuery boot
(function ($) {
    $(function () {

        // MAIN FUNCTIONS



        // STATUS & DATES

        // DatePicker initialisation as per documentation - https://bootstrap-datepicker.readthedocs.io/en/latest/
        $('.datepicker').datepicker({
            format: "dd/mm/yyyy",
            startView: 2,
            maxViewMode: 2,
            todayHighlight: true,
            autoclose: true
        });

        // Show FC, COD, PPA if relevant
        var showDates = function () {
            
            var status = $(this).val();
            console.log(status);
            var $dateFormGroup = $('.date-form-group');
            var $fcDate = $dateFormGroup.find('.fc').first();
            var $codDate = $dateFormGroup.find('.cod').first();
            var $ppaDate = $dateFormGroup.find('.ppa').first();

            if (status == 'fs') {
                $fcDate.hide();
                $codDate.hide();
                $ppaDate.hide();
            };

            if (status == 'fc') {
                $fcDate.hide();
                $codDate.hide();
                $ppaDate.hide();
            };

            if (status == 'con') {
                $fcDate.show();
                $codDate.hide();
                $ppaDate.hide();
            };

            if (status == 'ops') {
                $fcDate.show();
                $codDate.show();
                $ppaDate.show();
            };

            if (status == 'ext') {
                $fcDate.show();
                $codDate.show();
                $ppaDate.show();
            };

            if (status == 'dec') {
                $fcDate.show();
                $codDate.show();
                $ppaDate.show();
            };

                

        };
        $(document).ready(showDates);
        $(document).on('click', 'input:radio ', showDates);

        // PARTAKERS
        // Adds a TypeForm of component selected 
        var addPartakerFormGroup = function () {
            
                // Find relevant (multi)-form-group to clone (within)
                var $multipleFormGroup = $('.multiple-form-group.partakers');
                var $formGroup = $multipleFormGroup.find('.partakers-form-group').last();
                
                
                // Create clone and insert after last selected element
                var $formGroupClone = $formGroup.clone();
                $formGroupClone.insertAfter($formGroup);
            
                // Update input field's id and name to WTForm's requirements (types-#-id/name where # is the number of types form inputs)
                $formGroupClone.find('.form-control').each( (index, element) => {
                    console.log(element);
                    var prevId = $(element).attr('id').slice(0,-1);
                    console.log(prevId);
                    $(element).attr('id', prevId + (countFormGroup($multipleFormGroup)/2)); // Divide by 2 because there are two form-controls per formGroup
                    $(element).attr('name', prevId + (countFormGroup($multipleFormGroup)/2));
                    // Replace label (if any)
                    $label = $(element).parent().find('label');
                    if ($label) {
                        $label.attr('for', prevId + countFormGroup($multipleFormGroup));
                    }
                });
                
                // Show remove - button
                $('.btn-danger.remove-partaker').show();

                // Increase counter by 1
                var $counter = $('.counter-partaker');
                var counterValue = $counter.text();
                var counterInt = parseInt(counterValue);
                var newCounterInt = counterInt + 1;
                $counter.text(newCounterInt);

                // If form group has reached maximum, then disable add button
                if ($multipleFormGroup.data('max') <= countFormGroup($multipleFormGroup)/2) {
                    $('.btn-secondary.add-partaker').prop('disabled', true);
                
                }
        };

        // Adds last TypeForm of component selected 
        var removePartakerFormGroup = function () {
            
            var $multipleFormGroup = $('.multiple-form-group.partakers');
            var $formGroup = $multipleFormGroup.find('.partakers-form-group').last();
            $formGroup.remove();

            // Increase counter by 1
            var $counter = $('.counter-partaker');
            var counterValue = $counter.text();
            var counterInt = parseInt(counterValue);
            var newCounterInt = counterInt - 1;
            $counter.text(newCounterInt);

            // If form group is under  maximum, then enable add button
            if ($multipleFormGroup.data('max') > countFormGroup($multipleFormGroup)/2) {
                $('.btn-secondary.add-partaker').prop('disabled', false);
            }

            // If form group is equal to minimum, then hide remove button
            if ($multipleFormGroup.data('min') == countFormGroup($multipleFormGroup)/2) {
                $('.btn-danger.remove-partaker').hide();
            }
            
        };

        // Partakers listeners
        $(document).on('click', '.btn-secondary.add-partaker', addPartakerFormGroup);
        $(document).on('click', '.btn-danger.remove-partaker', removePartakerFormGroup);


        // TECHNOLOGY & COMPONENTS
        // Re-initialise by showing all component-group that are greater than 0

        // Adds or removes component form group depending on technology selected / deselected
        var technologyChangeState = function () {

            var $technologyGroup = $('.technology-form-group');
            var $componentFormGroup = $('.component-form-group');

            // Variable to hide (option) component form if no technologies are selected
            var anyTechnologiesChecked = false;
            var windTechnologiesChecked = false;
                        
            // Go through all technologies to check if they are selected
            $technologyGroup.find('input[type="checkbox"]').each( (index, element) => {
                
                // Variable used to find technological group 
                var techShortName = $(element).attr('name');

                if ($(element).is(":checked")) {
                    
                    // Display component part of the form
                    anyTechnologiesChecked = true;
                    $componentFormGroup.show();

                    // Had to resort to specifying windon and windoff because of class names conflicting (offshore would be calculated last out of the two in the lopp)
                    if (techShortName == 'windon' || techShortName == 'windoff'){
                        // Display specific technological components
                        windTechnologiesChecked = true;
                        var $componentGroup= $componentFormGroup.find('.component-group.wind').first();
                        $componentGroup.show();
                    } else {
                        // Display specific technological components
                        var $componentGroup= $componentFormGroup.find('.component-group.'+ techShortName);
                        $componentGroup.show();
                    }
                    
                // If techology is not checked
                } else {

                    if (techShortName == 'windon' || techShortName == 'windoff' ){
                        if (windTechnologiesChecked == false) {
                            // Hide specific technological components if unchecked
                            var $componentGroup= $componentFormGroup.find('.component-group.wind' );
                            $componentGroup.hide();
                        }
                    } else {
                        // Hide specific technological components if unchecked
                        var $componentGroup= $componentFormGroup.find('.component-group.'+ techShortName );
                        $componentGroup.hide();
                    }
                }
            });

            if (anyTechnologiesChecked == false) {
                $componentFormGroup.hide();
            }
                
        };

        $(document).ready(technologyChangeState);
        $(document).on('click', '#pv', technologyChangeState);
        $(document).on('click', '#csp', technologyChangeState);
        $(document).on('click', '#windon', technologyChangeState);
        $(document).on('click', '#windoff', technologyChangeState);
        $(document).on('click', '#wave', technologyChangeState);
        $(document).on('click', '#tidal', technologyChangeState);
        $(document).on('click', '#storage', technologyChangeState);


        // Adds a TypeForm of component selected 
        var addComponentFormGroup = function () {
            
            // Find component name
            var $formGroup = $(this).closest('.row');
            var $componentTitle = $formGroup.find('.title').first();
            var componentName = $componentTitle.text();

            // Clone a 'template' component-form-group that is always hidden
            var $typeFormGroupClone = $('.type-template-form-group').clone();
            
            // Update id and name of clone, depending on countFormGroup of relevant multi-form-group
            var $typeMultiFormGroup = $('.type-multiple-form-group');
            $typeFormGroupClone.attr('class', 'form-group type-form-subgroup-' + (countFormGroup($typeMultiFormGroup)) );

            // Update type-form title
            var $typeFormTitle = $typeFormGroupClone.find('.type-form-title');
            $typeFormTitle.text(componentName);

            // Fetch data from server to fill in drop down menus (type suppliers & models)
            // Request components from FilterComponents route
            $.getJSON('FilterTypes/' + componentName)
                // If sucessful
                .done( (data) => {

                    // Component (hidden field used for form submission)
                    var $typeFormComponent = $typeFormGroupClone.find('.form-control.type-component-form');
                    $typeFormComponent.val(data.component.id);


                    // Component Types
                    if (data.type) {

                        // Add response (components IDs and names) to type1 select field
                        $.each( data.type, (index, element) => {
                            var $typeFormType = $typeFormGroupClone.find('.form-control.type1');
                            $typeFormType.append('<option value =' + element.id + '>' + element.name + '</option>');
                        });
                    }

                    // Component Types
                    if (data.supplier) {

                        // Add response (components IDs and names) to type1 select field
                        $.each( data.supplier, (index, element) => {
                            var $typeFormSupplier = $typeFormGroupClone.find('.form-control.supplier');
                            $typeFormSupplier.append('<option value =' + element.id + '>' + element.name + '</option>');
                        });
                    }

                })

                // If failure
                .fail( (jqxhr, textStatus, error) => {
                    console.log('FAILED!');
                    var err = textStatus + ", " + error;
                    console.log( "Request Failed: " + err );
                    alert('JSON input cannot be computed by route! Contact Admin')
            });


            // Type 2 (currently only used for PV modules / PV cells)
            if (componentName=='PV Module'){
                // Fetch data from server to fill in drop down menus (type suppliers & models)
                // Request components from FilterComponents route
                $.getJSON('FilterTypes/PV Cell')
                // If sucessful
                .done( (data) => {

                    // Component Types
                    if (data.type) {

                            // Clone typeFormSubGroup (span including label & select field)
                        var $typeFormSubGroup = $typeFormGroupClone.find('.type-form-subgroup').first();
                        $typeFormType2SubGroup = $typeFormSubGroup.clone();

                        // Clear clone's select field
                        $typeFormType2 = $typeFormType2SubGroup.find('.form-control').first();
                        $typeFormType2.children().remove();

                        // Rename clone's ID, name and class
                        var prevId = $typeFormType2.attr('id').slice(0,12);
                        $typeFormType2.attr('id', prevId + '2');
                        $typeFormType2.attr('name', prevId + '2');
                        $typeFormType2.attr('class', 'form-control type2');

                        // Add response (components IDs and names) to clone's select field
                        $.each( data.type, (index, element) => {
                            $typeFormType2.append('<option value ="' + element.id + '">' + element.name + '</option>');
                        });

                        // Add clone to form
                        $typeFormSubGroup.parent().append($typeFormType2SubGroup);

                        // Update labels 
                        var $labelPlaceholder = $typeFormGroupClone.find("label[for='types-0-type1']").first();
                        $labelPlaceholder.text('PV Module Type');

                        var $labelPlaceholder = $typeFormType2SubGroup.find("label").first();
                        $labelPlaceholder.text('PV Cell Type');
                    }

                })

                // If failure
                .fail( (jqxhr, textStatus, error) => {
                    console.log('FAILED!');
                    var err = textStatus + ", " + error;
                    console.log( "Request Failed: " + err );
                    alert('JSON input cannot be computed by route! Contact Admin')
                });
            }
            
            

            
            // Find insertion point of component type multiple-form
            var $typeFormGroup = $('.type-form-input-group');

            // Insert into relevant multi-form-group (as last sub-form-group item)
            $typeFormGroup.append($typeFormGroupClone);

            // Update input field's id and name to WTForm's requirements (types-#-id/name where # is the number of types form inputs)
            $typeFormGroup.find('.form-group').each( (typeFormGroupCount , formGroup) => {
                // Replace types id & name
                $(formGroup).find('.form-control').each( (index, element) => {
                    // Keep endinf of id (made for 'types1' and 'types2')
                    var prevId = $(element).attr('id').slice(8);
                    $(element).attr('id', 'types-' + (typeFormGroupCount + 1) + '-' + prevId);
                    $(element).attr('name', 'types-' + (typeFormGroupCount + 1) + '-' + prevId);
                    // Replace label (if any)
                    $label = $(element).parent().find('label');
                    if ($label) {
                        $label.attr('for', 'types-' + (typeFormGroupCount + 1) + '-' + prevId);
                    }
                });
                
                // Replace suppliers id & name
                $(formGroup).find('.form-control').each( (index, element) => {
                    // Keep endinf of id (made for 'types1' and 'types2')
                    var prevId = $(element).attr('id').slice(8);
                    $(element).attr('id', 'types-' + (typeFormGroupCount + 1) + '-' + prevId);
                    $(element).attr('name', 'types-' + (typeFormGroupCount + 1) + '-' + prevId);
                    // Replace label (if any)
                    $label = $(element).parent().find('label');
                    if ($label) {
                        $label.attr('for', 'types-' + (typeFormGroupCount + 1) + '-' + prevId);
                    }
                });

            });
            
            // Show clone
            $typeFormGroupClone.show();

            // Find counter and increase value by 1
            var $counter = $formGroup.find('.counter').first();
            var counterValue = $counter.text();
            var counterInt = parseInt(counterValue);
            var newCounterInt = counterInt + 1;
            $counter.text(newCounterInt);

            // Make remove button appear
            var $removeButton = $formGroup.find('.remove').first();
            $removeButton.show();
   
        };

        // Adds last TypeForm of component selected 
        var removeComponentFormGroup = function () {

            // Find component name
            var $formGroup = $(this).closest('.row');
            var $componentTitle = $formGroup.find('.title').first();
            var componentName = $componentTitle.text();
            console.log(componentName);

            // Remove last component form with that name
            var $typeInputFormGroup = $('.type-form-input-group');
            console.log($typeInputFormGroup);
            // Passing by form title as componentName contains spaces (ie. can only match text element, not classes)
            var $lastTypeFormTitle = $typeInputFormGroup.find('.type-form-title:contains("'+ componentName + '")').last();
            var $typeFormGroup = $lastTypeFormTitle.parents('.form-group').first();
            console.log($typeFormGroup);
            $typeFormGroup.remove();

            // Find counter and decrease value by 1
            var $counter = $formGroup.find('.counter').first();
            var counterValue = $counter.text();
            var counterInt = parseInt(counterValue);
            var newCounterInt = counterInt - 1;
            $counter.text(newCounterInt);

            // Make remove button disappear if no forms
            if (newCounterInt == 0) {
                var $removeButton = $formGroup.find('.remove').first();
                $removeButton.hide();
            }
            
        };

        // Component TypesForm listeners
        $(document).on('click', '.btn-secondary.add', addComponentFormGroup);
        $(document).on('click', '.btn-danger.remove', removeComponentFormGroup);

        

        






        // HELPER FUNCTIONS

        // Find number of form-groups within multi-form-groups (usually)
        var countFormGroup = ($form) => {
            return $form.find('.form-group').length;
        };

        var countTypeFormGroup = ($form) => {
            // +1 because the template uses types-0-form
            return $form.find('.type-form-group').length + 1;
        }


        // LISTENERS



        // TODO ! -- ! -- If field.errors -> Show all remove buttons & last add button (disabled if required)
        //$(document).ready(componentInitialisation);



    });

    
})(jQuery);