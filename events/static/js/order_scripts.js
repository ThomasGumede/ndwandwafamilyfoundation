const ticket_types_inner_container = document.querySelector(
  "#ticket_types_inner_container"
);
const total_quantity = document.querySelector("#total_seats");
const id_quantity = document.querySelector("#id_quantity");
const id_total_price = document.querySelector("#id_total_price");
const total_price = document.querySelector("#total_price");
const submit_form = document.querySelector("#submit_form");
const tickets_form = document.querySelector("#tickets_form");
total_quantity.textContent = id_quantity.value;
id_total_price.value = total_price.textContent;

// load ticket types
window.addEventListener("load", () => {
  get_ticket_types();
});

function formatDate(date) {
  var options = { month: "short", day: "numeric", year: "numeric" };
  return date.toLocaleDateString("en-US", options);
}

submit_form.addEventListener("click", (e) => {
  e.preventDefault();
  if (parseInt(id_quantity.value) === 0) {
    alert("Please add at least 1 ticket type quantity");
  } else {
    tickets_form.submit();
  }
});

function get_ticket_types() {
  $.ajax({
    type: "GET",
    url: $("#ticket_types_container").data("tickets-url"),
    contentType: "application/json; charset=utf-8",
    cache: false,
    success: function (data) {
      if (data.success) {
        tickets_types = JSON.parse(data.event_ticket_types);
        
        tickets_types.forEach((ticket_type, index) => {
          let saleEndDate = new Date(ticket_type.fields.sale_end);
          let formattedSaleEndDate = formatDate(saleEndDate);
          ticket_types_inner_container.innerHTML += `
                            <div class="relative block bg-gray-50 p-4 border rounded-md">
                                <div class="space-y-4">
                                    <div class="flex flex-wrap gap-4 w-full md:items-center justify-between">
                                        
                                        <select class="hidden" name="form-${index}-ticket_type" id="id_form-${index}-ticket_type" value="${ticket_type.pk}">
                                            <option selected value="${ticket_type.pk}">${ticket_type.fields.title}</option>    
                                        </select>
                                        <div id="ticket_title">
                                            <h6 class="text-base">
                                                ${ticket_type.fields.title}
                                            </h6>
                              
                                            <p class="text-sm" id="form-${index}-price-text">
                                                R${ticket_type.fields.total_price}<span>(incl. R${ticket_type.fields.transaction_cost})</span> - ${ticket_type.fields.available_seats} seats available
                                            </p>
                                            <p class="text-sm" id="form-${index}-price-text">
                                                Ticket sale will end on <span id="sale-end-date">${formattedSaleEndDate}</span>
                                            </p>
                                        </div>
                                        <div class="bg-white border rounded-md w-fit p-3">
                                            <div class="flex items-center space-x-4">
                                                <div id="minus_quantity_${index}_${ticket_type.pk}" onclick="minus_quantity('quantity_text_${index}_${ticket_type.pk}', 'id_form-${index}-quantity')" class="cursor-pointer">
                                                    <i class="fa-solid fa-minus text-xl text-custom-h"></i>
                                                </div>
                                                <input type="number" value="0" class="w-[0.1px] h-[0.1px] opacity-0 overflow-hidden absolute -z-[1]" name="form-${index}-quantity" min="0" max="${ticket_type.fields.available_seats}" id="id_form-${index}-quantity">
                                                <div  id="quantity_container">
                                                    <p data-ticket-price='${ticket_type.fields.total_price}' id="quantity_text_${index}_${ticket_type.pk}" class="text-custom-h text-xl">0</p>
                                                </div>
                                                <div id="plus_quantity" onclick="add_quantity('quantity_text_${index}_${ticket_type.pk}', 'id_form-${index}-quantity')" class="cursor-pointer">
                                                    <i class="fa-solid fa-plus text-xl text-custom-h"></i>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                <div>
                            </div>
                        `;
        });

      } else {
        ticket_types = data;
      }
    },
    error: function (error) {
      alert("Something went wrong");
    },
  });
}

function add_quantity(quantity_text_id, quantity_input_id) {
  const quantity_text = document.querySelector(`#${quantity_text_id}`);
  const quantity_input = document.querySelector(`#${quantity_input_id}`);
  const text_price = parseFloat(
    quantity_text.getAttribute("data-ticket-price")
  );
  let total_ticket_price = text_price * parseFloat(quantity_input.value);

  if (parseInt(quantity_text.textContent) == 5) {
    alert("Sorry, you can only buy 5 tickets for each ticket type");

    quantity_text.textContent = 5;
    quantity_input.value = 5;
    // total_ticket_price = text_price * parseFloat(quantity_input.value);
  } else {
    quantity_text.textContent = parseInt(quantity_text.textContent) + 1;
    quantity_input.value = parseInt(quantity_input.value) + 1;
    id_quantity.value = parseInt(id_quantity.value) + 1;
    if (parseInt(quantity_text.textContent) <= 5) {
      total_ticket_price = text_price * 1;
      total_price.textContent =
        parseFloat(total_price.textContent) + total_ticket_price;
      id_total_price.value = total_price.textContent;
    }
  }

  total_quantity.textContent = id_quantity.value;
}

function minus_quantity(quantity_text_id, quantity_input_id) {
  const quantity_text = document.querySelector(`#${quantity_text_id}`);
  const quantity_input = document.querySelector(`#${quantity_input_id}`);
  const text_price = parseFloat(
    quantity_text.getAttribute("data-ticket-price")
  );
  let total_ticket_price = text_price * parseFloat(quantity_input.value);

  if (parseInt(quantity_text.textContent) === 0) {
    total_ticket_price = text_price * parseFloat(quantity_input.value);
    quantity_text.textContent = 0;
    quantity_input.value = 0;
  } else {
    total_ticket_price = text_price * 1;
    quantity_text.textContent = parseInt(quantity_text.textContent) - 1;
    quantity_input.value = parseInt(quantity_input.value) - 1;
    id_quantity.value = parseInt(id_quantity.value) - 1;
  }
  total_price.textContent =
    parseFloat(total_price.textContent) - total_ticket_price;
  id_total_price.value = total_price.textContent;
  total_quantity.textContent = id_quantity.value;
}
