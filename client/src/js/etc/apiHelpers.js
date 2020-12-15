/**
 * Convert a JS object into GET URL parameters
 * Returns string. 
 * 
 * @param base Base URL atop which to add GET parameters
 * @param params Object to insert into a URL string
 */
export function makeUrl(base, params = {}) {
  if (Object.keys(params).length > 0) {
    let out = base + "?";

    Object.keys(params).forEach(k => {
      out += k;
      out += "=";
      out += params[k];
      out += "&";
    });
    return out.replace(/&$/g, "");
  } else {
    return base;
  }
}

/**
 * Convert object information the message for a POST request
 */
export const toPayload = toSend => {
  return {
    method: "POST",
    body: JSON.stringify(toSend),
    headers: {
      "Content-type": "application/json; charset=UTF-8"
    }
  };
};
