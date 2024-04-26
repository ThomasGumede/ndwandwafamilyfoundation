const add_ticket_type = document.querySelector("#add_ticket_type");
const forms_container = document.querySelector("#forms_container");
const id_form_total = document.querySelector("#id_form-TOTAL_FORMS");
const delete_form = document.querySelector(".delete_current_form");
const total_seats = document.querySelector("#total_seats");
let form_count = 0;
let max_forms = parseInt(forms_container.getAttribute("data-max-forms")) - 1;

add_ticket_type.addEventListener("click", () => {
    
    if(max_forms > 0){
      form_count += 1;
      max_forms -= 1;
      
      id_form_total.value = parseInt(id_form_total.value) + 1;
      forms_container.innerHTML += `
            <div id="form_content_${form_count}" class="w-full mb-2 p-4 relative block">
                <div class="flex flex-wrap gap-4">
                    <div class="w-full lg:w-4/12 md:px-4">
                        <div class="relative w-full mb-3">
                            <label for="id_form-${form_count}-title">
                                ticket name*
                            </label>
                            <input type="text" name="form-${form_count}-title" class="block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150" maxlength="250" id="id_form-${form_count}-title">
                            <span class="text-[11px] text-custom-tertiary block font-normal lowercase">Enter ticket type</span>

                        </div>
                    </div>
                    <div class="w-full lg:w-4/12 md:px-4">
                        <div class="relative w-full mb-3">
                            <label for="id_form-${form_count}-price"> Price* </label>
                            <input value="" id="id_form-${form_count}-price" name="form-${form_count}-price" type="number" class="block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150">
                            <span class="text-[11px] text-custom-tertiary block font-normal lowercase"></span>

                        </div>
                    </div>
                    <div class="w-full lg:w-3/12 md:px-4">
                        <div class="relative w-full mb-3">
                            <label for="id_form-${form_count}-available_seats">
                                total seats*
                            </label>
                            <input id="id_form-${form_count}-available_seats" name="form-${form_count}-available_seats" type="number" min="0" class="block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150">
                            <span class="text-[11px] text-custom-tertiary block font-normal lowercase"></span>

                        </div>
                    </div>
                    <div class="w-full lg:w-5/12 md:px-4">
                        <div class="relative w-full mb-3">
                            <label for="id_form-${form_count}-sale_start">
                                ticket sale start date*
                            </label>
                            <input type="text" name="form-${form_count}-sale_start" class="block ticket_datetime p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150" maxlength="250" id="id_form-${form_count}-title">
                            <span class="text-[11px] text-custom-tertiary block font-normal lowercase">Enter ticket type</span>

                        </div>
                    </div>
                    <div class="w-full lg:w-5/12 md:px-4">
                        <div class="relative w-full mb-3">
                            <label for="id_form-${form_count}-sale_end">
                                ticket sale start date*
                            </label>
                            <input type="text" name="form-${form_count}-sale_end" class="block ticket_datetime p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150" maxlength="250" id="id_form-${form_count}-title">
                            <span class="text-[11px] text-custom-tertiary block font-normal lowercase">Enter ticket type</span>

                        </div>
                    </div>
                </div>
                <div class="absolute top-4 right-4  bg-current">
                    <div data-formid="form_content_${form_count}" onclick="delete_ticket_form('form_content_${form_count}')" class="grid items-center group justify-center delete_current_form cursor-pointer">
                        <i class="fa-solid fa-trash group-hover:scale-105 text-2xl text-custom-h"></i>
                    </div>
                </div>
            </div>
            <hr class="mb-4 border-b-1 border-gray-300" />
        `;
    }else{
        alert("You have reached the maximun number of ticket types required")
    }
});

function delete_ticket_form(form_id) {
  let form = document.querySelector(`#${form_id}`);
  forms_container.removeChild(form);
  id_form_total.value = parseInt(id_form_total.value) - 1;
}



    

