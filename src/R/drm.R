make_drm <- function(
  data,
  dose=c("", ""),
  response=c("", ""),
  data_sub=c(),
  max_response=0,
  min_response=NULL,
  dose_predict=c(0),
  save_plot_to=""
) {

  #' create, plot and predict a drm based on input data format used very
  #' often in my analysis.
  #' dose, response   should be character vecors, which define columns
  #'                  of data in the first index and more descriptive names at
  #'                  the second index for the plot
  #' subset           optional, if applicable can be used to filter a subset
  #'                  out of a specific column of the main data set
  #'                  useage: data_sub=c("example_column", "example_condition")
  #' max_response     parameter passed to log_logistc function of DRM, defaults
  #'                  to zero, which means that the maximum response is 0.
  #'                  This is only useful for decreasing DRCs.
  #' min_response     This parameter defines Null response, can be a limit
  #'                  in time of death observations, or the maximal value
  #' dose_predict     optional, pass any vector of doses for which, normalized
  #'                  and absolute responses should be predicted


  if (length(data_sub) != 0) {
    for (i in seq_along(data_sub)) {
        data <- subset(data, data[, names(data_sub)[[i]]] == data_sub[[i]])
    }
  }

  ds <- data
  df <- data.frame(
    dose = ds[, dose[1]],
    response = ds[, response[1]]
  )

  if (is.null(min_response)) {
    min_response <- max(df[, "response"])
  }

  max_response_normed <- max_response / min_response
  df[, "response_normalized"] <- df[, "response"] / min_response

  # DRM UVB model with log-logistic fit
  drm_norm <- drc::drm(
    response_normalized ~ dose,
    data = df,
    fct = drc::LL.4(fixed = c(b = NA, c = max_response_normed, d = 1, e = NA))
  )

  drm_absolute <- drc::drm(
    response ~ dose,
    data = df,
    fct = drc::LL.4(
      fixed = c(b = NA, c = max_response, d = min_response, e = NA)
    )
  )

  # plot model
  if (nchar(save_plot_to) > 0) {
    dir.create(save_plot_to, recursive = TRUE)
    png(file.path(save_plot_to, paste0(dose[1], ".png")))
  }
  plot(
    drm_norm,
    ylim = c(0, 1), xlim = c(0, max(df[, "dose"] * 2)),
    xlab = dose[2],
    ylab = paste0(
      response[2],
      " (normalized to ", round(max(df[, "response"])), ")"
    )
  )
  if (nchar(save_plot_to) > 0) dev.off()

  pred_norm <- 1 - predict(
    drm_norm,
    data.frame(dose = dose_predict)
  )

  pred_absolute <- predict(
    drm_absolute,
    data.frame(dose = dose_predict)
  )

  predictions <- data.frame(
    dose = dose_predict,
    prediction_normalized = pred_norm,
    prediction_absolute = pred_absolute
  )

  return(
    list(
      input_data = df,
      drm_normalized = drm_norm,
      drm_absolute = drm_absolute,
      predictions = predictions
    )
  )

}
